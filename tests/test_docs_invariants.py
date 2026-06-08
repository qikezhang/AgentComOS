from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def test_agents_contains_core_invariants():
    text = (ROOT / "AGENTS.md").read_text()
    assert "GM never calls Workers" in text
    assert "Hermes Worker is a tmux-launched Hermes CLI instance" in text
    assert "Decision Market and Feynman adoption is staged" in text
    assert "development_explicit" in text
    assert "industrial_auto" in text
