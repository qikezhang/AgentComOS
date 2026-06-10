from agentcomos.executor_decision import ExecutorDecision

def test_executor_decision_init():
    dec = ExecutorDecision(executor_request_id="req1", decision="blocked", reason="policy_missing")
    assert dec.decision == "blocked"
    assert dec.reason == "policy_missing"
    assert dec.execution_mode == "dry_run"
