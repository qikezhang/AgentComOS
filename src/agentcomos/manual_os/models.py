from dataclasses import dataclass, field
from typing import List, Optional, Literal

@dataclass
class CommandProposal:
    command: str
    purpose: str = ""
    requires_sudo: bool = False
    destructive: bool = False

@dataclass
class RequestedAction:
    title: str = ""
    description: str = ""
    risk_level: str = "low"
    proposed_commands: List[CommandProposal] = field(default_factory=list)

@dataclass
class RequestSafety:
    auto_execute: bool = False
    requires_human_approval: bool = True
    real_runtime_used: bool = False
    agent_executed_shell: bool = False
    agent_executed_ssh: bool = False
    agent_executed_sudo: bool = False
    agent_executed_docker: bool = False
    agent_executed_systemctl: bool = False
    system_modified_by_agent: bool = False

@dataclass
class ManualOsRequest:
    run_id: str
    task_id: str
    phase: str = "G10_MANUAL_OS_CONTROLLED_ADOPTION"
    status: Literal["requested", "already_current"] = "requested"
    manual_os_required: bool = True
    requested_action: RequestedAction = field(default_factory=RequestedAction)
    safety: RequestSafety = field(default_factory=RequestSafety)

@dataclass
class ApprovalScope:
    commands_allowed: List[str] = field(default_factory=list)
    max_duration_minutes: int = 30
    requires_result_report: bool = True

@dataclass
class ApprovalSafety:
    approval_is_explicit: bool = True
    auto_execute: bool = False
    agent_executed_shell: bool = False

@dataclass
class ManualOsApproval:
    run_id: str
    task_id: str
    status: Literal["approved", "rejected"]
    phase: str = "G10_MANUAL_OS_CONTROLLED_ADOPTION"
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    reason: Optional[str] = None
    approved_at: str = ""
    approval_scope: ApprovalScope = field(default_factory=ApprovalScope)
    safety: ApprovalSafety = field(default_factory=ApprovalSafety)

@dataclass
class CommandReport:
    command: str
    result: str = ""
    exit_code: int = 0

@dataclass
class ResultSafety:
    result_is_reported: bool = True
    system_execution_was_manual: bool = True
    agent_executed_shell: bool = False
    agent_executed_ssh: bool = False
    agent_executed_sudo: bool = False
    agent_executed_docker: bool = False
    agent_executed_systemctl: bool = False

@dataclass
class ManualOsResult:
    run_id: str
    task_id: str
    status: Literal["completed", "failed", "skipped"]
    executed_by: str
    summary: str
    phase: str = "G10_MANUAL_OS_CONTROLLED_ADOPTION"
    commands_reported: List[CommandReport] = field(default_factory=list)
    safety: ResultSafety = field(default_factory=ResultSafety)
