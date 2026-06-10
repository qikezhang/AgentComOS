from agentcomos.executor_policy import ExecutorPolicy

def test_missing_policy_denies():
    policy = ExecutorPolicy.load("non_existent_policy.yaml")
    assert policy is None

def test_loaded_policy_evaluates_source():
    data = {"allowed_sources": ["discord"]}
    policy = ExecutorPolicy(data)
    assert policy.is_source_allowed("discord") is True
    assert policy.is_source_allowed("gm") is False
