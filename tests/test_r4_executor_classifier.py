from agentcomos.executor_classifier import ExecutorClassifier

def test_secret_request_blocked():
    risk, status, reason = ExecutorClassifier.classify_command("show token=abc")
    assert risk == "secret"
    assert status == "blocked"

def test_destructive_command_blocked():
    risk, status, reason = ExecutorClassifier.classify_command("docker system prune -f")
    assert risk == "destructive"
    assert status == "blocked"

def test_direct_system_command_blocked():
    commands = ["bash -c 'echo hi'", "ssh user@host", "sudo ls", "systemctl status", "docker run alpine"]
    for cmd in commands:
        risk, status, reason = ExecutorClassifier.classify_command(cmd)
        assert risk == "direct_system"
        assert status == "blocked"

def test_restart_requires_approval():
    risk, status, reason = ExecutorClassifier.classify_command("restart service app")
    assert risk == "high"
    assert status == "requires_approval"

def test_status_read_only_classified():
    risk, status, reason = ExecutorClassifier.classify_command("status")
    assert risk == "read_only"
    assert status == "received"
    
def test_unknown_blocked():
    risk, status, reason = ExecutorClassifier.classify_command("do magical things")
    assert risk == "unknown"
    assert status == "blocked"

def test_docker_compose_restart_blocked():
    risk, status, reason = ExecutorClassifier.classify_command("docker compose restart")
    assert risk == "direct_system"
    assert status == "blocked"
