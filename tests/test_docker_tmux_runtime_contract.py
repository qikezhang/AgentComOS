from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_runtime_tmux_installs_tmux_and_terminfo():
    text = (ROOT / "docker" / "Dockerfile.runtime-tmux").read_text(encoding="utf-8")
    assert "tmux" in text
    assert "ncurses-term" in text
    assert "ENV TERM=xterm-256color" in text


def test_compose_runtime_tmux_satisfies_tty_and_persistence():
    data = yaml.safe_load((ROOT / "docker" / "docker-compose.runtime-tmux.yml").read_text(encoding="utf-8"))
    svc = data["services"]["agentcomos-runtime"]
    assert svc["tty"] is True
    assert svc["stdin_open"] is True
    assert svc["environment"]["TERM"] == "xterm-256color"
    assert "tail -f /dev/null" in " ".join(svc["command"])
    assert svc["restart"] == "unless-stopped"
