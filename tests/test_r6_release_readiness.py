from agentcomos.release_readiness import check_release_readiness

def test_release_readiness():
    res = check_release_readiness()
    assert "status" in res
    assert "blockers" in res
    assert "warnings" in res
