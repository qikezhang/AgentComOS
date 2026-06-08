from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v286_active_docs_are_consistent():
    active = [
        "RELEASE_MANIFEST.md",
        "docs/04_DEVELOPMENT_ROADMAP.md",
        "docs/05_ACCEPTANCE_MATRIX.md",
        "docs/09_RUNTIME_PROFILES.md",
        "docs/15_CODEX_ANTIGRAVITY_COLLABORATION.md",
        "docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md",
        "docs/17_PHASED_DELIVERY_PLAN.md",
        "docs/18_ACCEPTANCE_GATES.md",
        "docs/21_COMMERCIAL_DEPLOYMENT_READINESS.md",
        "docs/22_RUNTIME_INSTALLATION_EVOLUTION.md",
        "docs/23_PR_AND_REVIEW_WORKFLOW.md",
    ]
    for rel in active:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "v2.8.6" in text or "AgentComOS v2.8.6" in text or "Phase" in text or "Gate" in text
        assert "Decision Market and Feynman default flow" not in text


def test_controller_first_is_documented_for_antigravity():
    text = (ROOT / "docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md").read_text(encoding="utf-8")
    for term in ["agentcomos run create", "agentcomos controller tick", "events.jsonl", "幂等"]:
        assert term in text


def test_runtime_evolution_keeps_docker_tmux_experimental():
    text = (ROOT / "docs/22_RUNTIME_INSTALLATION_EVOLUTION.md").read_text(encoding="utf-8")
    assert "Docker 负责安装" in text
    assert "systemd" in text
    assert "experimental" in text
