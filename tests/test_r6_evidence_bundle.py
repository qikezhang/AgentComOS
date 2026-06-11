from agentcomos.production_smoke import create_evidence_bundle

def test_evidence_bundle(tmp_path):
    bundle = create_evidence_bundle(tmp_path)
    assert "git_branch" in bundle
    assert (tmp_path / "manifest.yaml").exists()
