from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_active_docs_policy_and_product_spec_overlay_exist():
    active = (ROOT / "docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md").read_text(encoding="utf-8")
    product = (ROOT / "docs/00_PRODUCT_SPEC_V2_8.md").read_text(encoding="utf-8")
    assert "Active Implementation Documents" in active
    assert "Historical Reference Documents" in active
    assert "Conflict Resolution" in active
    assert "本文件是 **AgentComOS v2.8 完整产品目标基线**" in product
    assert "docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md" in product


def test_historical_docs_are_archived_not_active_policy():
    for rel in ["docs/11_ENGINEERING_CONTRACT_V2_8_3.md", "docs/13_CONTRACT_HARDENING_V2_8_4.md"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "Archived" in text or "归档" in text
        assert "不作为 Antigravity 实施" in text
    assert (ROOT / "docs/archive/11_ENGINEERING_CONTRACT_V2_8_3.md").exists()
    assert (ROOT / "docs/archive/13_CONTRACT_HARDENING_V2_8_4.md").exists()


def test_all_g0_to_g11_acceptance_reports_exist():
    expected = [
        "G0_CONTRACT_BASELINE.md",
        "G1_CONTROLLER_MINIMUM_STATE_MACHINE.md",
        "G2_FAKE_OPENCODE_RUNTIME.md",
        "G3_REAL_OPENCODE_RUNTIME_MANAGER.md",
        "G4_TMUX_HERMES_WORKER_POOL_FAKE_E2E.md",
        "G5_REAL_HERMES_WORKER_RUNTIME.md",
        "G6_EVIDENCE_DELIVERY_GM_REPORT.md",
        "G7_SIMPLE_OPERATING_PROGRAM.md",
        "G8_DECISION_FEYNMAN_CONTROLLED_ADOPTION.md",
        "G9_LOOP_EXECUTION_TASK_FRONTIER.md",
        "G10_MANUAL_WORKER_EVOLUTION_AUTO_VERSIONER.md",
        "G11_INDUSTRIAL_AUTO_GOVERNANCE.md",
    ]
    for name in expected:
        path = ROOT / "codex/acceptance-reports" / name
        assert path.exists(), name
        text = path.read_text(encoding="utf-8")
        assert "Status" in text
        assert "Codex Findings" in text
        assert "Next Gate Unlock Status" in text


def test_phase_acceptance_reporting_assigns_codex_all_phases():
    text = (ROOT / "docs/25_PHASE_ACCEPTANCE_REPORTING.md").read_text(encoding="utf-8")
    assert "Codex 不只负责 G0/G1" in text
    assert "G11_INDUSTRIAL_AUTO_GOVERNANCE.md" in text
    assert "每个 Phase" in text


def test_g1_to_g2_handoff_blocks_fake_opencode_until_g1_passes():
    text = (ROOT / "docs/26_G1_TO_G2_HANDOFF.md").read_text(encoding="utf-8")
    assert "G1 acceptance report = passed" in text
    assert "G2 只实现 Fake OpenCode Runtime" in text
    task = (ROOT / "antigravity/tasks/phase-2-fake-opencode-runtime.md").read_text(encoding="utf-8")
    assert "Locked Until" in task
    assert "Do not integrate real OpenCode" in task


def test_v286_release_manifest_mentions_ordered_next_steps():
    text = (ROOT / "RELEASE_MANIFEST.md").read_text(encoding="utf-8")
    assert "v2.8.6" in text
    for phrase in ["Codex G0", "Antigravity", "all Phase", "Fake OpenCode"]:
        assert phrase in text
