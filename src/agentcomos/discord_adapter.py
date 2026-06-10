import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

from agentcomos.discord_config import load_discord_config
from agentcomos.discord_redaction import redact_string, redact_data
from agentcomos.discord_commands import DiscordCommandParser
from agentcomos.discord_permissions import PermissionEvaluator
from agentcomos.discord_idempotency import check_duplicate, record_message
from agentcomos.discord_artifacts import (
    save_artifact,
    append_audit,
    DiscordInboundMessage,
    GMCommand,
    DiscordOutboundMessage,
    DiscordAudit
)

async def status_check(connect_check: bool = False) -> Dict[str, Any]:
    """Returns the adapter status."""
    config = load_discord_config()
    token_present = config.is_token_available()
    
    status_data = {
        "config_loaded": True,
        "enabled": config.enabled,
        "token_present": token_present,
        "connected": False,
        "connection_checked": False,
    }
    
    if not token_present:
        status_data["reason"] = "token_missing"
    elif not connect_check:
        status_data["reason"] = "connect_check_not_requested"
    else:
        status_data["connection_checked"] = True
        try:
            from agentcomos.discord_runtime import check_discord_connection
            is_connected = await check_discord_connection()
            status_data["connected"] = is_connected
            if not is_connected:
                status_data["reason"] = "connect_check_failed"
        except Exception as e:
            status_data["connected"] = False
            status_data["reason"] = f"connect_check_error: {str(e)}"
            
    return status_data

def ingest_test(message_data: Dict[str, Any], runtime_dir: Path) -> Dict[str, Any]:
    """
    Ingests a single message (for test).
    Message structure expected:
    {
        "message_id": "...",
        "guild_id": "...",
        "channel_id": "...",
        "author_id_hash": "...",
        "roles": ["..."],
        "content": "..."
    }
    """
    config = load_discord_config()
    
    message_id = message_data.get("message_id", str(uuid.uuid4()))
    content_redacted = redact_string(message_data.get("content", ""))
    now_str = datetime.now(timezone.utc).isoformat()
    
    inbound_artifact = DiscordInboundMessage(
        message_id=message_id,
        guild_id=message_data.get("guild_id", ""),
        channel_id=message_data.get("channel_id", ""),
        author_id_hash=message_data.get("author_id_hash", ""),
        role_names_or_hashes=message_data.get("roles", []),
        content_redacted=content_redacted,
        received_at=now_str
    )

    duplicate_record = check_duplicate(runtime_dir, message_id)
    if duplicate_record:
        inbound_artifact.duplicate_of = duplicate_record.get("message_id")
        save_artifact(runtime_dir, "discord_inbound_message.yaml", inbound_artifact)
        
        audit = DiscordAudit(
            timestamp=now_str,
            inbound_message_id=message_id,
            duplicate=True,
            permission_decision="skipped",
            permission_reason="duplicate_message",
            command_type="none",
            command_risk="none",
            outbound_status="duplicate"
        )
        append_audit(runtime_dir, audit)
        return {"status": "duplicate", "gm_command_id": duplicate_record.get("gm_command_id")}

    save_artifact(runtime_dir, "discord_inbound_message.yaml", inbound_artifact)

    parser = DiscordCommandParser(default_mode=config.default_command_mode)
    parsed_cmd = parser.parse(message_data.get("content", ""))
    
    evaluator = PermissionEvaluator(config)
    permission_result = evaluator.evaluate(
        message_id=message_id,
        guild_id=inbound_artifact.guild_id,
        channel_id=inbound_artifact.channel_id,
        user_hash=inbound_artifact.author_id_hash,
        roles=inbound_artifact.role_names_or_hashes,
        command_risk=parsed_cmd["risk_level"]
    )
    
    save_artifact(runtime_dir, "permission_result.yaml", permission_result)

    gm_command_id = None
    outbound_status = "sent"
    outbound_reply_content = ""
    
    if permission_result.decision == "allowed":
        gm_command_id = f"gmc_{uuid.uuid4().hex[:12]}"
        
        status = "accepted"
        requires_executor = False
        requires_approval = False
        
        if parsed_cmd["risk_level"] in ["high", "controlled_write"]:
            requires_executor = True
            requires_approval = True
            status = "requires_executor"
            outbound_reply_content = f"Command {parsed_cmd['command_type']} requires executor (R4/R5 pending)."
        elif parsed_cmd["risk_level"] == "read_only":
            requires_executor = False
            requires_approval = False
            status = "accepted"
            outbound_reply_content = f"Read-only command {parsed_cmd['command_type']} accepted."
            
        gm_cmd = GMCommand(
            gm_command_id=gm_command_id,
            source_message_id=message_id,
            command_type=parsed_cmd["command_type"],
            command_text_redacted=content_redacted,
            risk_level=parsed_cmd["risk_level"],
            requires_executor=requires_executor,
            requires_approval=requires_approval,
            status=status,
            created_at=now_str
        )
        save_artifact(runtime_dir, "gm_command.yaml", gm_cmd)

        if requires_executor or parsed_cmd["risk_level"] == "read_only":
            from agentcomos.executor_request import ExecutorRequest
            from agentcomos.executor_framework import ExecutorFramework
            from agentcomos.executor_config import ExecutorConfig
            from agentcomos.executor_policy import ExecutorPolicy

            exe_config = ExecutorConfig()
            policy = ExecutorPolicy.load(exe_config.policy_path) if exe_config.policy_path else None
            framework = ExecutorFramework(exe_config, policy)
            
            req = ExecutorRequest(
                source="discord",
                command_type=gm_cmd.command_type,
                command_text_redacted=gm_cmd.command_text_redacted,
                requested_by_hash=inbound_artifact.author_id_hash,
                source_message_id=message_id,
                target=None,
                risk_level=gm_cmd.risk_level,
                requires_executor=gm_cmd.requires_executor,
                requires_approval=gm_cmd.requires_approval,
                correlation_id=gm_cmd.gm_command_id,
            )
            framework.process_request(req, str(runtime_dir))
    else:
        # Blocked
        blocked_reason = permission_result.reason
        if permission_result.reason == "command_unknown" and "blocked_reason" in parsed_cmd:
            blocked_reason = parsed_cmd["blocked_reason"]
            
        outbound_reply_content = f"Request blocked. Reason: {blocked_reason}"
        outbound_status = "sent_blocked_notice"

        gm_command_id = f"gmc_{uuid.uuid4().hex[:12]}"
        gm_cmd = GMCommand(
            gm_command_id=gm_command_id,
            source_message_id=message_id,
            command_type=parsed_cmd["command_type"],
            command_text_redacted=content_redacted,
            risk_level=parsed_cmd["risk_level"],
            requires_executor=False,
            requires_approval=False,
            status="blocked",
            created_at=now_str,
            blocked_reason=blocked_reason
        )
        save_artifact(runtime_dir, "gm_command.yaml", gm_cmd)

    outbound_artifact = DiscordOutboundMessage(
        outbound_id=f"out_{uuid.uuid4().hex[:12]}",
        source_message_id=message_id,
        channel_id=inbound_artifact.channel_id,
        status="success",
        content_redacted=outbound_reply_content,
        created_at=now_str,
        delivery_status="simulated"
    )
    save_artifact(runtime_dir, "discord_outbound_message.yaml", outbound_artifact)
    
    audit = DiscordAudit(
        timestamp=now_str,
        inbound_message_id=message_id,
        duplicate=False,
        permission_decision=permission_result.decision,
        permission_reason=permission_result.reason,
        command_type=parsed_cmd["command_type"],
        command_risk=parsed_cmd["risk_level"],
        outbound_status=outbound_status
    )
    append_audit(runtime_dir, audit)

    record_message(runtime_dir, message_id, gm_command_id)

    return {
        "status": "processed",
        "permission_decision": permission_result.decision,
        "gm_command_id": gm_command_id
    }
