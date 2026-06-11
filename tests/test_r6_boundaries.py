from agentcomos.production_smoke import run_production_smoke

def test_no_real_execution(tmp_path):
    res = run_production_smoke(tmp_path)
    assert res["results"]["real_execution_check"] == "pass"
