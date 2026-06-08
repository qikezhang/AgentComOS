from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_codex_antigravity_collaboration_doc_exists():
    text = (ROOT / "docs/15_CODEX_ANTIGRAVITY_COLLABORATION.md").read_text(encoding="utf-8")
    assert "Codex" in text and "Antigravity" in text
    assert "Definition of Done" in text


def test_controller_is_first_priority_documented():
    text = (ROOT / "docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md").read_text(encoding="utf-8")
    assert "Controller" in text
    assert "Run State Machine" in text
    assert "幂等" in text


def test_phased_delivery_plan_keeps_v28_features():
    text = (ROOT / "docs/17_PHASED_DELIVERY_PLAN.md").read_text(encoding="utf-8")
    for term in ["Controller", "OpenCode", "Hermes", "Loop", "Manual", "Worker Evolution", "Industrial Auto"]:
        assert term in text


def test_decision_feynman_adoption_policy_has_three_stages():
    text = (ROOT / "docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md").read_text(encoding="utf-8")
    assert "development_explicit" in text
    assert "transition_assisted" in text
    assert "industrial_auto" in text
