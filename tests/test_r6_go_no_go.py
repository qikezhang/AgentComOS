import pytest
from agentcomos.production_smoke import evaluate_go_no_go

def test_go_no_go_missing_evidence_is_no_go():
    res = evaluate_go_no_go({}, {"status": "pass"})
    assert res["status"] == "no_go"
    assert "missing_evidence" in res
    assert len(res["missing_evidence"]) > 0

def test_go_no_go_shallow_self_generated_evidence_is_no_go():
    res = evaluate_go_no_go({"status": "pass"}, {"status": "pass"})
    assert res["status"] == "no_go"

def test_go_no_go_missing_r2_r5_refs_is_no_go():
    res = evaluate_go_no_go({"status": "pass", "evidence_refs": {"R2": "pass"}}, {"status": "pass"})
    assert res["status"] == "no_go"
    assert "incomplete R2-R5 refs" in res["missing_evidence"]

def test_go_no_go_missing_boundary_scan_is_no_go():
    rr = {"status": "pass", "evidence_refs": {"R2": "1", "R3": "2", "R4": "3", "R5": "4"}, "command_summaries": {}}
    res = evaluate_go_no_go(rr, {"status": "pass"})
    assert res["status"] == "no_go"
    assert "boundary_summary" in res["missing_evidence"]

def test_go_no_go_missing_secret_scan_is_no_go():
    rr = {"status": "pass", "evidence_refs": {"R2": "1", "R3": "2", "R4": "3", "R5": "4"}, "command_summaries": {}, "boundary_summary": "pass"}
    res = evaluate_go_no_go(rr, {"status": "pass"})
    assert res["status"] == "no_go"
    assert "secret_scan_summary" in res["missing_evidence"]

def test_go_no_go_missing_rollback_is_no_go():
    rr = {"status": "pass", "evidence_refs": {"R2": "1", "R3": "2", "R4": "3", "R5": "4"}, "command_summaries": {}, "boundary_summary": "pass", "secret_scan_summary": "pass"}
    res = evaluate_go_no_go(rr, {"status": "pass"})
    assert res["status"] == "no_go"
    assert "rollback_readiness" in res["missing_evidence"]

def test_go_no_go_failed_smoke_is_no_go():
    rr = {"status": "pass", "evidence_refs": {"R2": "1", "R3": "2", "R4": "3", "R5": "4"}, "command_summaries": {}, "boundary_summary": "pass", "secret_scan_summary": "pass", "rollback_readiness": "pass", "operator_runbook_readiness": "pass"}
    res = evaluate_go_no_go(rr, {"status": "fail"})
    assert res["status"] == "no_go"
    assert "Smoke report failed" in res["blockers"]

def test_go_no_go_all_hard_gates_pass_go():
    rr = {"status": "pass", "evidence_refs": {"R2": "1", "R3": "2", "R4": "3", "R5": "4"}, "command_summaries": {"h": "pass"}, "boundary_summary": "pass", "secret_scan_summary": "pass", "rollback_readiness": "pass", "operator_runbook_readiness": "pass", "docker_availability": "pass"}
    res = evaluate_go_no_go(rr, {"status": "pass"})
    assert res["status"] == "go"

def test_go_no_go_docker_unavailable_conditional_only_when_recorded():
    rr = {"status": "pass", "evidence_refs": {"R2": "1", "R3": "2", "R4": "3", "R5": "4"}, "command_summaries": {"h": "pass"}, "boundary_summary": "pass", "secret_scan_summary": "pass", "rollback_readiness": "pass", "operator_runbook_readiness": "pass", "docker_availability": "unavailable"}
    res = evaluate_go_no_go(rr, {"status": "pass"})
    assert res["status"] == "conditional_go"
