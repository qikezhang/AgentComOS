from agentcomos.release_readiness import check_release_readiness

def test_no_secrets():
    res = check_release_readiness()
    assert not any("Real secret" in b for b in res["blockers"])

def test_recursive_env_guard_detects_nested_env(tmp_path):
    from agentcomos.production_smoke import assert_no_raw_env_files
    nested_dir = tmp_path / "a" / "b"
    nested_dir.mkdir(parents=True)
    env_file = nested_dir / ".env"
    env_file.write_text("SECRET=123")
    violations = assert_no_raw_env_files(tmp_path)
    assert len(violations) == 1
    assert str(env_file) in violations[0]

def test_env_example_allowed_but_env_forbidden(tmp_path):
    from agentcomos.production_smoke import assert_no_raw_env_files
    (tmp_path / ".env.example").write_text("TEMPLATE=1")
    violations = assert_no_raw_env_files(tmp_path)
    assert len(violations) == 0

