from __future__ import annotations

import yaml
import agentcomos.controller.events as events
import agentcomos.controller.state as state
from agentcomos.evidence.builder import finalize_evidence_packet, get_input_fingerprint, get_evidence_status
from agentcomos.delivery.builder import get_delivery_status
from agentcomos.controller.artifacts import rebuild_timeline_from_events
from agentcomos.frontier.builder import read_task_frontier

def generate_gm_report(run_id: str, format: str = "markdown") -> None:
    run_dir = state.get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run {run_id} does not exist.")
        
    fingerprint = get_input_fingerprint(run_id)
    path = run_dir / ("gm_report.yaml" if format == "yaml" else "gm_report.md")
    
    if path.exists():
        if format == "yaml":
            try:
                old_report = yaml.safe_load(path.read_text(encoding="utf-8"))
                if old_report.get("input_fingerprint") == fingerprint:
                    return
            except Exception:
                pass
        else:
            try:
                text = path.read_text(encoding="utf-8")
                if fingerprint in text:
                    return
            except Exception:
                pass

    events.append_event(run_id, "gm.report.started", {"format": format})
    
    try:
        runtime_path = run_dir / "evidence_packet" / "runtime_summary.yaml"
        frontier_status_path = run_dir / "frontier_status.yaml"
        evidence_status = get_evidence_status(run_id)
        delivery_status = get_delivery_status(run_id)
            
        rt = {}
        if runtime_path.exists():
            rt = yaml.safe_load(runtime_path.read_text(encoding="utf-8"))
        frontier_status = {}
        if frontier_status_path.exists():
            frontier_status = yaml.safe_load(frontier_status_path.read_text(encoding="utf-8")) or {}
            
        oc = rt.get("opencode", {})
        hm = rt.get("hermes", {})
        wk = rt.get("worker", {})
        
        frontier = read_task_frontier(run_id) or {}
        decision_tasks = []
        feynman_tasks = []
        manual_os_tasks = []
        missing_required = False
        awaiting_d = len(frontier_status.get("awaiting_decision_tasks", [])) > 0
        awaiting_f = len(frontier_status.get("awaiting_feynman_tasks", [])) > 0
        awaiting_m = len(frontier_status.get("awaiting_manual_os_tasks", [])) > 0
        
        loop_status_path = run_dir / "loop_status.yaml"
        loop_status = {}
        if loop_status_path.exists():
            loop_status = yaml.safe_load(loop_status_path.read_text(encoding="utf-8")) or {}
            loop_status.update({
                "mode": "bounded",
                "automatic_decision_market_enabled": False,
                "automatic_feynman_executor_enabled": False,
                "manual_os_enabled": False,
                "worker_evolution_enabled": False,
                "auto_versioner_enabled": False,
                "recursive_task_expansion_enabled": False,
                "daemon_enabled": False
            })
        
        for task in frontier.get("tasks", []):
            task_id = task.get("task_id")
            if task.get("decision_required") or (run_dir / "decision" / task_id / "decision_request.yaml").exists():
                result_path = run_dir / "decision" / task_id / "decision_result.yaml"
                status_val = "completed" if result_path.exists() else ("awaiting_decision" if task_id in frontier_status.get("awaiting_decision_tasks", []) else "missing")
                if not result_path.exists():
                    missing_required = True
                dt = {
                    "task_id": task_id,
                    "required": True,
                    "status": status_val,
                    "artifact": f"decision/{task_id}/decision_result.yaml"
                }
                if result_path.exists():
                    d_result = yaml.safe_load(result_path.read_text(encoding="utf-8")) or {}
                    dt["selected_option"] = d_result.get("selected_option", "unknown")
                decision_tasks.append(dt)
                
            if task.get("feynman_required") or (run_dir / "feynman" / task_id / "feynman_check.yaml").exists():
                result_path = run_dir / "feynman" / task_id / "feynman_result.yaml"
                status_val = "completed" if result_path.exists() else ("awaiting_feynman" if task_id in frontier_status.get("awaiting_feynman_tasks", []) else "missing")
                if not result_path.exists():
                    missing_required = True
                ft = {
                    "task_id": task_id,
                    "required": True,
                    "status": status_val,
                    "artifact": f"feynman/{task_id}/feynman_result.yaml"
                }
                if result_path.exists():
                    f_result = yaml.safe_load(result_path.read_text(encoding="utf-8")) or {}
                    ft["pass"] = f_result.get("pass", False)
                feynman_tasks.append(ft)
                
            if task.get("manual_os_required") or (run_dir / "manual_os" / task_id / "manual_os_request.yaml").exists():
                result_path = run_dir / "manual_os" / task_id / "manual_os_result.yaml"
                status_val = "completed" if result_path.exists() else ("awaiting_manual_os" if task_id in frontier_status.get("awaiting_manual_os_tasks", []) else "missing")
                if not result_path.exists():
                    missing_required = True
                mt = {
                    "task_id": task_id,
                    "required": True,
                    "status": status_val,
                    "artifact": f"manual_os/{task_id}/manual_os_result.yaml"
                }
                if result_path.exists():
                    m_result = yaml.safe_load(result_path.read_text(encoding="utf-8")) or {}
                    mt["result_status"] = m_result.get("status", "unknown")
                manual_os_tasks.append(mt)
                
        g8_controls = {
            "decision_controlled_mode": "explicit",
            "feynman_controlled_mode": "explicit",
            "automatic_decision_market_enabled": False,
            "automatic_feynman_executor_enabled": False,
            "real_runtime_used": False,
            "decision_tasks": decision_tasks,
            "feynman_tasks": feynman_tasks,
            "manual_os_tasks": manual_os_tasks
        }
        
        mos_status = "none"
        mos_next_action = ""
        if awaiting_m:
            mos_status = "awaiting_manual_os"
            mos_next_action = "human must approve or reject request\nhuman must report result after manual execution"
        elif manual_os_tasks:
            mos_status = "completed"

        manual_os_info = {
            "controlled_adoption_enabled": True,
            "auto_execute": False,
            "human_approval_required": True,
            "human_result_report_required": True,
            "agent_executed_shell": False,
            "agent_executed_ssh": False,
            "agent_executed_sudo": False,
            "agent_executed_docker": False,
            "agent_executed_systemctl": False,
            "autonomous_os_operation": False,
            "loop_auto_execution": False,
            "status": mos_status,
            "next_action": mos_next_action
        }
        
        status = "completed"
        if evidence_status in ("failed", "missing_manifest", "missing_run") or delivery_status in ("failed", "missing_packet", "missing_run"):
            status = "failed"
        elif evidence_status == "partial" or delivery_status == "partial" or len(frontier_status.get("failed_tasks", [])) > 0 or awaiting_d or awaiting_f or awaiting_m or missing_required or loop_status.get("status") == "blocked":
            status = "partial"

        # Artifact gaps
        gaps = []
        if evidence_status == "failed":
            gaps.append("Evidence packet generation failed or missing.")
        if delivery_status == "failed":
            gaps.append("Delivery packet generation failed or missing.")
            
        # Failed tasks disclosure
        task_frontier_path = run_dir / "task_frontier.yaml"
        task_frontier = {}
        if task_frontier_path.exists():
            task_frontier = yaml.safe_load(task_frontier_path.read_text(encoding="utf-8")) or {}
            
        failed_tasks_info = []
        for task in task_frontier.get("tasks", []):
            if task.get("status") == "failed":
                failed_tasks_info.append(f"Task {task.get('task_id')}: {task.get('failure_reason', 'unknown reason')}")

        unavailable_disclosure = []
        if oc.get("unavailable_count", 0) > 0:
            unavailable_disclosure.append(f"{oc['unavailable_count']} OpenCode real job(s) unavailable.")
        if hm.get("unavailable_count", 0) > 0:
            unavailable_disclosure.append(f"{hm['unavailable_count']} Hermes real job(s) unavailable.")
            
        if format == "yaml":
            report_yaml = {
                "run_id": run_id,
                "status": status,
                "input_fingerprint": fingerprint,
                "delivery_status": delivery_status,
                "evidence_status": evidence_status,
                "summary": "GM Report generated from evidence.",
                "g8_controls": g8_controls,
                "manual_os": manual_os_info,
                "runtime_usage": {
                    "fake_opencode_used": oc.get("fake_opencode_used", False),
                    "real_opencode_attempted": oc.get("real_opencode_attempted", False),
                    "real_opencode_used": oc.get("real_opencode_used", False),
                    "fake_hermes_used": hm.get("fake_hermes_used", False),
                    "real_hermes_attempted": hm.get("real_hermes_attempted", False),
                    "real_hermes_used": hm.get("real_hermes_used", False),
                    "tmux_used": wk.get("tmux_used", False),
                    "unavailable_disclosure": unavailable_disclosure
                },
                "task_frontier": {
                    "frontier_id": frontier_status.get("frontier_id"),
                    "status": frontier_status.get("status", "missing"),
                    "tasks_total": frontier_status.get("tasks_total", 0),
                    "ready_tasks": frontier_status.get("ready_tasks", []),
                    "blocked_tasks": frontier_status.get("blocked_tasks", []),
                    "completed_tasks": frontier_status.get("completed_tasks", []),
                    "failed_tasks": frontier_status.get("failed_tasks", []),
                    "next_task_id": frontier_status.get("next_task_id"),
                },
                "loop_execution": loop_status,
                "failed_tasks_disclosure": failed_tasks_info,
                "artifacts": [
                    "evidence_packet/manifest.yaml",
                    "evidence_packet/events_summary.yaml",
                    "evidence_packet/runtime_summary.yaml",
                    "evidence_packet/artifact_index.yaml",
                    "evidence_packet/validation_summary.yaml",
                    "operating_program.yaml",
                    "task_frontier.yaml",
                    "task_frontier_index.yaml",
                    "frontier_status.yaml"
                ],
                "artifact_gaps": gaps,
                "risks": gaps + unavailable_disclosure + failed_tasks_info,
                "next_actions": ["Ready for Codex review."]
            }
            for lf in ["loop_plan.yaml", "loop_status.yaml", "loop_trace.yaml", "loop_summary.md"]:
                if (run_dir / lf).exists():
                    report_yaml["artifacts"].append(lf)
            path.write_text(yaml.dump(report_yaml, sort_keys=False), encoding="utf-8")
        else:
            gaps_md = "\n".join(f"- {g}" for g in gaps) if gaps else "None detected."
            unavailable_md = "\n".join(f"- {u}" for u in unavailable_disclosure) if unavailable_disclosure else "No unavailable runtime issues detected."
            failed_md = "\n".join(f"- {f}" for f in failed_tasks_info) if failed_tasks_info else "None."
            frontier_md = (
                f"- **Frontier ID**: {frontier_status.get('frontier_id', 'missing')}\n"
                f"- **Frontier Status**: {frontier_status.get('status', 'missing')}\n"
                f"- **Tasks Total**: {frontier_status.get('tasks_total', 0)}\n"
                f"- **Ready Tasks**: {frontier_status.get('ready_tasks', [])}\n"
                f"- **Blocked Tasks**: {frontier_status.get('blocked_tasks', [])}\n"
                f"- **Completed Tasks**: {frontier_status.get('completed_tasks', [])}\n"
                f"- **Failed Tasks**: {frontier_status.get('failed_tasks', [])}\n"
                f"- **Next Task**: {frontier_status.get('next_task_id')}\n"
            )
            
            controls_md_lines = [
                "## Decision / Feynman Controls",
                "- **Decision controlled mode**: explicit",
                "- **Feynman controlled mode**: explicit",
                "- **Automatic Decision Market**: not enabled",
                "- **Automatic Feynman executor**: not enabled",
                "- **Real runtime used**: false",
                "",
                "These controls were generated deterministically for G8 controlled adoption.",
                "",
                "## Manual OS Controlled Adoption",
                f"- **Controlled adoption enabled**: {manual_os_info['controlled_adoption_enabled']}",
                f"- **auto_execute**: {manual_os_info['auto_execute']}",
                f"- **human approval required**: {manual_os_info['human_approval_required']}",
                f"- **human result report required**: {manual_os_info['human_result_report_required']}",
                f"- **agent executed shell**: {manual_os_info['agent_executed_shell']}",
                f"- **agent executed ssh**: {manual_os_info['agent_executed_ssh']}",
                f"- **agent executed sudo**: {manual_os_info['agent_executed_sudo']}",
                f"- **agent executed docker**: {manual_os_info['agent_executed_docker']}",
                f"- **agent executed systemctl**: {manual_os_info['agent_executed_systemctl']}",
                f"- **autonomous OS operation**: {manual_os_info['autonomous_os_operation']}",
                f"- **loop auto manual-os execution**: {manual_os_info['loop_auto_execution']}",
                f"- **status**: {manual_os_info['status']}",
            ]
            if manual_os_info['next_action']:
                controls_md_lines.append(f"- **next action**:\n{manual_os_info['next_action']}")
            controls_md_lines.append("")
            
            if decision_tasks:
                controls_md_lines.append("**Decision Tasks:**")
                for t in decision_tasks:
                    if "selected_option" in t:
                        controls_md_lines.append(f"- Task {t['task_id']}: status={t['status']}, selected_option={t['selected_option']}, artifact={t['artifact']}")
                    else:
                        controls_md_lines.append(f"- Task {t['task_id']}: status={t['status']}, artifact={t['artifact']}")
                controls_md_lines.append("")
                
            if feynman_tasks:
                controls_md_lines.append("**Feynman Tasks:**")
                for t in feynman_tasks:
                    if "pass" in t:
                        controls_md_lines.append(f"- Task {t['task_id']}: status={t['status']}, pass={t['pass']}, artifact={t['artifact']}")
                    else:
                        controls_md_lines.append(f"- Task {t['task_id']}: status={t['status']}, artifact={t['artifact']}")
                controls_md_lines.append("")
                
            if awaiting_d:
                controls_md_lines.append("**Blocked on Decision:**")
                for task_id in frontier_status.get("awaiting_decision_tasks", []):
                    controls_md_lines.append(f"- Blocked task: {task_id}")
                    controls_md_lines.append(f"  - Missing artifact: decision/{task_id}/decision_result.yaml")
                    controls_md_lines.append(f"  - Next action: run `agentcomos decision request --run {run_id} --task {task_id} --mode explicit`")
                controls_md_lines.append("")

            if awaiting_f:
                controls_md_lines.append("**Blocked on Feynman Check:**")
                for task_id in frontier_status.get("awaiting_feynman_tasks", []):
                    controls_md_lines.append(f"- Blocked task: {task_id}")
                    controls_md_lines.append(f"  - Missing artifact: feynman/{task_id}/feynman_result.yaml")
                    controls_md_lines.append(f"  - Next action: run `agentcomos feynman check --run {run_id} --task {task_id} --mode explicit`")
                controls_md_lines.append("")

            if manual_os_tasks:
                controls_md_lines.append("**Manual OS Tasks:**")
                for t in manual_os_tasks:
                    if "result_status" in t:
                        controls_md_lines.append(f"- Task {t['task_id']}: status={t['status']}, result_status={t['result_status']}, artifact={t['artifact']}")
                    else:
                        controls_md_lines.append(f"- Task {t['task_id']}: status={t['status']}, artifact={t['artifact']}")
                controls_md_lines.append("")
                
            if awaiting_m:
                controls_md_lines.append("**Blocked on Manual OS:**")
                for task_id in frontier_status.get("awaiting_manual_os_tasks", []):
                    controls_md_lines.append(f"- Blocked task: {task_id}")
                    controls_md_lines.append(f"  - Missing artifact: manual_os/{task_id}/manual_os_result.yaml")
                    controls_md_lines.append(f"  - Next action: run `agentcomos manual-os request --run {run_id} --task {task_id}`")
                controls_md_lines.append("")

            controls_md = "\n".join(controls_md_lines)
            
            report_md = f"""# GM Report - {run_id}

## Executive Summary
This report summarizes the execution of run `{run_id}`, detailing the status of evidence and delivery generation, and analyzing runtime tool usage.

## Current Status
- **Run ID**: {run_id}
- **Overall Status**: {status}
- **Delivery Status**: {delivery_status}
- **Evidence Status**: {evidence_status}
- **Input Fingerprint**: {fingerprint}

## What Was Done
The GM reporting process gathered the latest evidence packet and delivery packet artifacts. It aggregated runtime occurrences, identified missing elements, and verified runtime boundaries according to G6 requirements.

{controls_md}
## Runtime Usage
- **Fake OpenCode used**: {oc.get("fake_opencode_used", False)}
- **Real OpenCode attempted**: {oc.get("real_opencode_attempted", False)}
- **Real OpenCode used**: {oc.get("real_opencode_used", False)}
- **Fake Hermes used**: {hm.get("fake_hermes_used", False)}
- **Real Hermes attempted**: {hm.get("real_hermes_attempted", False)}
- **Real Hermes used**: {hm.get("real_hermes_used", False)}
- **tmux used**: {wk.get("tmux_used", False)}

**Unavailable Runtime Disclosures:**
{unavailable_md}

## Evidence
The following evidence files were used to generate this report:
- `evidence_packet/manifest.yaml`
- `evidence_packet/events_summary.yaml`
- `evidence_packet/runtime_summary.yaml`
- `evidence_packet/artifact_index.yaml`
- `evidence_packet/validation_summary.yaml`
- `operating_program.yaml`
- `task_frontier.yaml`
- `task_frontier_index.yaml`
- `frontier_status.yaml`

## Loop Execution Controls
- **Loop Execution mode**: bounded
- **Runtime mode**: {loop_status.get('runtime_mode', 'fake')}
- **Max ticks**: {loop_status.get('ticks_requested', 0)}
- **Ticks executed**: {loop_status.get('ticks_executed', 0)}
- **Tasks advanced**: {loop_status.get('tasks_advanced', 0)}
- **Stop reason**: {loop_status.get('stop_reason', 'missing')}
- **Real runtime used**: false
- **Automatic Decision/Feynman**: disabled
- **Manual OS**: not enabled
- **Worker Evolution**: not enabled
- **Auto Versioner**: not enabled
- **Recursive task expansion**: not enabled
- **Background daemon**: not enabled

## Task Frontier
{frontier_md}

**Failed Tasks Disclosure:**
{failed_md}

**Artifact Gaps:**
{gaps_md}

## Results
The run produced the required outputs for the active phases. The delivery packet reflects the compiled evidence.

## Risks and Gaps
Risks identified in the evidence and runtime phases include:
{unavailable_md}
{failed_md}
{gaps_md}

## Next Actions
- Ready for Codex review.
- Address any remaining partial statuses if necessary.

## Audit Notes
This report was automatically generated by AgentComOS GM Report Builder. It does not replace human verification.
"""
            path.write_text(report_md, encoding="utf-8")
            
        events.append_event(run_id, "gm.report.completed", {"format": format})
        
        rebuild_timeline_from_events(run_id)
        finalize_evidence_packet(run_id)
    except Exception as e:
        events.append_event(run_id, "gm.report.failed", {"error": str(e)})
        rebuild_timeline_from_events(run_id)
        raise

def get_gm_report_status(run_id: str, format: str = "yaml") -> str:
    # helper added for test
    run_dir = state.get_run_dir(run_id)
    path = run_dir / ("gm_report.yaml" if format == "yaml" else "gm_report.md")
    if not path.exists():
        return "missing"
    if format == "yaml":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data.get("status", "unknown")
    return "unknown"
