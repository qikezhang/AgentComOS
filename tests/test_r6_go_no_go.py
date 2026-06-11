from agentcomos.production_smoke import evaluate_go_no_go

def test_go_no_go():
    rr = {"status": "pass", "blockers": []}
    sr = {"status": "pass"}
    res = evaluate_go_no_go(rr, sr)
    assert res["status"] == "go"
    
    sr2 = {"status": "fail"}
    res2 = evaluate_go_no_go(rr, sr2)
    assert res2["status"] == "no_go"
