# G8 - Decision/Feynman Controlled Adoption Acceptance Report

## Status

failed

## Audit Metadata

- Audit time: 2026-06-09 14:57:11 CST
- Auditor: Codex
- Branch reviewed: `antigravity/g8-decision-feynman-controlled-adoption`
- Commit reviewed: `1bad0d9e2c678116817737a1ca1aeb5b6c452b58`
- Prior Codex report commit: `11b608698fa742c4f5d00bc70f004c8b9f809f9a`
- CLI note: direct `agentcomos` console script was unavailable in this shell, so equivalent commands were executed with `PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli`.

## Inputs Reviewed

- `AGENTS.md`
- `docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md`
- `docs/17_PHASED_DELIVERY_PLAN.md`
- `docs/18_ACCEPTANCE_GATES.md`
- `docs/20_DATA_LEDGER_EVENT_MODEL.md`
- `docs/21_COMMERCIAL_DEPLOYMENT_READINESS.md`
- `docs/modules/06_operating_program_task_frontier.md`
- `docs/modules/07_decision_feynman_controlled_adoption.md`
- `docs/templates/decision_request.yaml`
- `docs/templates/decision_result.yaml`
- `docs/templates/feynman_check.yaml`
- `docs/templates/feynman_result.yaml`
- `antigravity/tasks/phase-8-decision-feynman-controlled-adoption.md`
- G8 source and tests in the branch diff, including the `1bad0d9` reporting integration fix.

## Commands Executed

```bash
git fetch origin
git checkout antigravity/g8-decision-feynman-controlled-adoption
git pull origin antigravity/g8-decision-feynman-controlled-adoption
git status --short
git log --oneline -12
git diff --name-status origin/main...HEAD
grep -R "Loop Execution\|recursive task\|subagent\|Manual OS\|Worker Evolution\|Auto Versioner\|Decision Market executor\|Feynman executor\|automatic decision\|auto decision\|auto feynman" src tests scripts docs antigravity codex || true
grep -R "opencode serve\|opencode run\|run --attach\|hermes chat\|tmux new-session\|tmux send-keys\|discord\|Discord" src tests scripts || true
grep -R "pass\|assert True" tests/test_g8* || true
make compile
make test
make validate-examples
```

Manual acceptance commands were also executed for G1-G7 regression, G8 Decision/Feynman explicit mode, Task Frontier blocking/unblocking, reporting integration, and runtime artifact cleanup.

## Validation Results

- `make compile`: passed.
- `make test`: passed, `279 passed in 12.88s`.
- `make validate-examples`: passed.
- Empty G8 tests: failed. `tests/test_g8_reporting_integration.py` contains pass-only placeholders:
  - `test_g8_delivery_completed_when_required_results_exist`
  - `test_g8_gm_report_completed_when_required_results_exist`

## G1-G7 Regression Results

- G1 Controller: passed. Clean run create/status/tick/recover completed; recover returned state `accepted`.
- G2 Fake OpenCode: passed. Fake submit/status/collect completed for `OCJ-OI-TECHAI8-001-001`.
- G3 OpenCode availability: passed. Command did not crash and reported OpenCode available on this machine with version `unknown`.
- G4 Fake Hermes Worker: passed. Fake worker start/status/collect completed and kept fake tmux/Hermes semantics.
- G5 Hermes availability: passed. Command did not crash and reported `available: False`, `reason: hermes not found`.
- G6 Evidence / Delivery / GM Report regression: passed. Evidence, delivery, and GM markdown/yaml generation completed.
- G7 Program / Frontier: passed. TF-001, TF-002, and TF-003 completed in order; fourth tick returned `no_ready_task`, not loop execution.

## G8 Positive Results

- Decision request: passed. `decision_request.yaml` and `decision_result.yaml` generated for `TF-001`.
- Decision status/result: passed and read-only.
- Decision explicit mode fields: passed. Result had `mode: explicit`, `status: completed`, `real_runtime_used: false`, `selected_option`, `rationale`, and `risks`.
- Decision events/timeline: passed. `decision.requested` and `decision.completed` appeared in `events.jsonl` and `timeline.yaml`.
- Feynman check: passed. `feynman_check.yaml` and `feynman_result.yaml` generated for `TF-001`.
- Feynman status/result: passed and read-only.
- Feynman explicit mode fields: passed. Result had `mode: explicit`, `status: completed`, `real_runtime_used: false`, `pass: true`, `explanation`, `detected_ambiguities`, `missing_inputs`, and `execution_risks`.
- Feynman events/timeline: passed. `feynman.check.started` and `feynman.check.completed` appeared in `events.jsonl` and `timeline.yaml`.

## G8 Negative Results

- Decision missing mode: passed, failed with exit code 2.
- Decision invalid `auto` mode: passed, failed with exit code 2.
- Decision missing run: passed, failed with exit code 2 and created no orphan run directory.
- Decision missing task: passed, failed with exit code 2 and created no orphan task artifact.
- Feynman missing mode: passed, failed with exit code 2.
- Feynman invalid `auto` mode: passed, failed with exit code 2.
- Feynman missing run: passed, failed with exit code 2 and created no orphan run directory.
- Feynman missing task: passed, failed with exit code 2 and created no orphan task artifact.

## Frontier Blocking Results

- `decision_required: true` without result: passed. TF-001 became `awaiting_decision`; controller tick returned `no_ready_task`; no decision artifacts were auto-created.
- Decision result unblocking: passed. Explicit decision request unblocked TF-001 after frontier status refresh.
- `feynman_required: true` without result: passed. TF-002 became `awaiting_feynman`; controller tick did not execute it; no feynman artifacts were auto-created.
- Feynman result unblocking: passed. Explicit feynman check unblocked TF-002 after frontier status refresh.
- `pass: false` feynman fixture: passed in previous review and covered by G8 frontier tests.

## Reporting Integration Results

- Evidence artifact index: passed. It now indexes:
  - `decision/TF-001/decision_request.yaml`
  - `decision/TF-001/decision_result.yaml`
  - `feynman/TF-001/feynman_check.yaml`
  - `feynman/TF-001/feynman_result.yaml`
  - G8 phase labels are present for those artifacts.
- Delivery integration: passed for core G8 requirements. `delivery_packet.yaml` includes G8 artifacts and `g8_controls`; completed required results produced `status: completed` after frontier status refresh.
- GM report integration: passed for core G8 requirements. `gm_report.md` and `gm_report.yaml` disclose explicit Decision mode, explicit Feynman mode, deterministic controlled G8 mode, `real_runtime_used: false`, no automatic Decision Market, and no automatic Feynman executor.
- Awaiting Decision/Feynman status: passed. With required results missing, delivery and GM report status were `partial`, not `completed`, and controller tick did not auto-create artifacts.
- Note: `delivery_packet.yaml` still says `Ready for Codex G6 review.` in `next_actions`; this is stale wording and should be cleaned up, but the core G8 reporting contract now passes.

## Idempotency Results

- Decision and Feynman core artifact hashes were stable across repeated explicit commands in the prior review.
- `decision.completed` and `feynman.check.completed` were not duplicated in the prior review.
- `decision status`, `decision result`, `feynman status`, and `feynman result` remain read-only.

## Boundary Check

- Branch diff did not include `.agentcomos/runs`, `uv.lock`, `reproduce*.sh`, or `reproduce*.log`.
- Branch diff did not include G0-G7 acceptance report status changes.
- Branch diff did not include G9+ implementation files.
- Boundary grep found historical docs/tests and existing G3/G4/G5 command builders, not a new G8 real runtime path.
- Real OpenCode called by G8: no.
- Real Hermes called by G8: no.
- Discord/user communication: no.
- Loop Execution implemented by G8: no.
- Recursive task expansion implemented by G8: no.
- Subagent delegation implemented by G8: no.
- Manual OS implemented by G8: no.
- Worker Evolution implemented by G8: no.
- Auto Versioner implemented by G8: no.
- Decision Market executor automation implemented by G8: no.
- Feynman executor automation implemented by G8: no.

## Blocking Issues

1. G8 still contains pass-only test placeholders. The acceptance checklist explicitly requires checking empty tests and failing G8 if `pass` or `assert True` is an empty placeholder. Two tests in `tests/test_g8_reporting_integration.py` are placeholders:
   - `test_g8_delivery_completed_when_required_results_exist` ends with `pass # we test what we can` and has no assertion for the completed delivery status it names.
   - `test_g8_gm_report_completed_when_required_results_exist` ends with `pass` and has no assertion for completed GM status.

## Resolved Since Prior Failed Review

- Prior issue 1, artifact index missing G8 artifacts: resolved.
- Prior issue 2, delivery missing G8 artifacts/controls: resolved for artifacts and controls. Stale G6 next-action wording remains as a non-blocking cleanup item.
- Prior issue 3, GM report missing G8 disclosures: resolved.
- Prior issue 4, awaiting Decision/Feynman allowing completed reporting status: resolved.
- Prior issue 5, missing reporting tests: partially resolved. Reporting tests were added, but two of them are empty placeholders and remain blocking.

## Non-Blocking Notes

- `origin/main` currently tracks a partial `.agentcomos/runs/OI-TECHAI8-001` baseline (`run_status.yaml`, events/timeline, delivery/manifest) without `operating_intent.yaml`. Clean run setup was used for equivalent behavioral verification. No `.agentcomos/runs` diff is introduced by this G8 branch.
- After generating Decision/Feynman results, a frontier status refresh is needed before delivery/GM reads the run as fully unblocked. The refreshed path passed.

## Runtime Artifact Cleanup

Cleanup performed:

```bash
rm -rf .agentcomos/runs/OI-TECHAI8-001
rm -rf .agentcomos/runs/OI-MISSING-INTENT
git restore --source origin/main -- .agentcomos/runs
rm -rf .agentcomos/worker-runtime
find . -maxdepth 1 \( -name 'uv.lock' -o -name 'reproduce*.sh' -o -name 'reproduce*.log' \) -delete
```

Post-cleanup checks:

- `.agentcomos/runs` not present in `origin/main...HEAD` diff.
- `uv.lock` not present in `origin/main...HEAD` diff.
- `git status --short` was clean before this report update.

## Decision

G8 failed.

G9 Loop Execution remains locked. Antigravity must replace the pass-only G8 tests with real assertions and re-request Codex review.

## Next Gate Unlock Status

Locked. G9 may not start until G8 is re-reviewed and this report is marked `passed`.
