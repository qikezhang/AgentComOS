from agentcomos.release_readiness import check_release_readiness

def test_no_secrets():
    res = check_release_readiness()
    assert not any("Real secret" in b for b in res["blockers"])
