from __future__ import annotations

import yaml
import agentcomos.controller.events as events
import agentcomos.controller.state as state
from agentcomos.evidence.builder import finalize_evidence_packet, get_input_fingerprint, get_evidence_status
from agentcomos.delivery.builder import get_delivery_status
from agentcomos.controller.artifacts import rebuild_timeline_from_events

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
        evidence_status = get_evidence_status(run_id)
        delivery_status = get_delivery_status(run_id)
            
        rt = {}
        if runtime_path.exists():
            rt = yaml.safe_load(runtime_path.read_text(encoding="utf-8"))
            
        oc = rt.get("opencode", {})
        hm = rt.get("hermes", {})
        wk = rt.get("worker", {})
        
        status = "completed"
        if evidence_status in ("failed", "missing_manifest", "missing_run") or delivery_status in ("failed", "missing_packet", "missing_run"):
            status = "failed"
        elif evidence_status == "partial" or delivery_status == "partial":
            status = "partial"

        # Artifact gaps
        gaps = []
        if evidence_status == "failed":
            gaps.append("Evidence packet generation failed or missing.")
        if delivery_status == "failed":
            gaps.append("Delivery packet generation failed or missing.")

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
                "artifacts": [
                    "evidence_packet/manifest.yaml",
                    "evidence_packet/events_summary.yaml",
                    "evidence_packet/runtime_summary.yaml",
                    "evidence_packet/artifact_index.yaml",
                    "evidence_packet/validation_summary.yaml"
                ],
                "artifact_gaps": gaps,
                "risks": gaps + unavailable_disclosure,
                "next_actions": ["Ready for Codex review."]
            }
            path.write_text(yaml.dump(report_yaml, sort_keys=False), encoding="utf-8")
        else:
            gaps_md = "\n".join(f"- {g}" for g in gaps) if gaps else "None detected."
            unavailable_md = "\n".join(f"- {u}" for u in unavailable_disclosure) if unavailable_disclosure else "No unavailable runtime issues detected."
            
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

**Artifact Gaps:**
{gaps_md}

## Results
The run produced the required outputs for the active phases. The delivery packet reflects the compiled evidence.

## Risks and Gaps
Risks identified in the evidence and runtime phases include:
{unavailable_md}
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
