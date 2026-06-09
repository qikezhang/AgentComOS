# G8 - Decision/Feynman Controlled Adoption Acceptance Report

## Status

passed

## Audit Metadata

- Audit time: 2026-06-09 15:15:22 CST
- Auditor: Codex
- Branch reviewed: `antigravity/g8-decision-feynman-controlled-adoption`
- Commit reviewed: `a0668f9929f78246e771873a7c906fe9a54d42a1`
- Prior Codex report commit: `06bf1f4b01f9efd4192759c6812ac3b603d0ca67`
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
- G8 source and tests in the branch diff, including the `a0668f9` test fix.

## Commands Executed

```bash
git fetch origin
git checkout antigravity/g8-decision-feynman-controlled-adoption
git pull origin antigravity/g8-decision-feynman-controlled-adoption
git status --short
git log --oneline -8
git diff --name-status origin/main...HEAD
grep -R "pass\|assert True" tests/test_g8* || true
grep -R "Loop Execution\|recursive task\|subagent\|Manual OS\|Worker Evolution\|Auto Versioner\|Decision Market executor\|Feynman executor\|automatic decision\|auto decision\|auto feynman" src tests scripts docs antigravity codex || true
grep -R "opencode serve\|opencode run\|run --attach\|hermes chat\|tmux new-session\|tmux send-keys\|discord\|Discord" src tests scripts || true
make compile
make test
make validate-examples
```

Manual acceptance commands were also executed for focused G8 Decision/Feynman explicit artifacts, Task Frontier blocking/unblocking, reporting integration, and runtime artifact cleanup.

## Validation Results

- `make compile`: passed.
- `make test`: passed, `279 passed in 12.38s`.
- `make validate-examples`: passed.
- Empty G8 tests: passed. The prior pass-only placeholders were replaced with assertions in `tests/test_g8_reporting_integration.py`; current grep only finds test names containing `passed` and YAML data keys `pass: true/false`.

## G1-G7 Regression Results

- G1 Controller: passed in the prior focused regression on this branch.
- G2 Fake OpenCode: passed in the prior focused regression on this branch.
- G3 OpenCode availability: passed in the prior focused regression on this branch.
- G4 Fake Hermes Worker: passed in the prior focused regression on this branch.
- G5 Hermes availability: passed in the prior focused regression on this branch.
- G6 Evidence / Delivery / GM Report regression: passed in the prior focused regression on this branch.
- G7 Program / Frontier: passed in the prior focused regression on this branch; TF-001, TF-002, and TF-003 completed in order and the fourth tick returned `no_ready_task`.

## G8 Positive Results

- Decision request: passed. `decision_request.yaml` and `decision_result.yaml` generated for `TF-001`.
- Decision status/result: passed and read-only.
- Decision explicit mode fields: passed. Result had `mode: explicit`, `status: completed`, `real_runtime_used: false`, `selected_option`, `rationale`, and `risks`.
- Decision events/timeline: passed. `decision.completed` appeared in `events.jsonl`.
- Feynman check: passed. `feynman_check.yaml` and `feynman_result.yaml` generated for `TF-001`.
- Feynman status/result: passed and read-only.
- Feynman explicit mode fields: passed. Result had `mode: explicit`, `status: completed`, `real_runtime_used: false`, `pass: true`, `explanation`, `detected_ambiguities`, `missing_inputs`, and `execution_risks`.
- Feynman events/timeline: passed. `feynman.check.completed` appeared in `events.jsonl`.

## G8 Negative Results

- Decision missing mode: passed in prior review.
- Decision invalid `auto` mode: passed in prior review.
- Decision missing run: passed in prior review.
- Decision missing task: passed in prior review.
- Feynman missing mode: passed in prior review.
- Feynman invalid `auto` mode: passed in prior review.
- Feynman missing run: passed in prior review.
- Feynman missing task: passed in prior review.

## Frontier Blocking Results

- `decision_required: true` without result: passed. TF-001 became `awaiting_decision`; controller tick returned `no_ready_task`; no decision artifacts were auto-created.
- Decision result unblocking: passed after explicit decision request and frontier status refresh.
- `feynman_required: true` without result: passed. Required feynman result absence did not auto-create artifacts or run the task.
- Feynman result unblocking: passed after explicit feynman check and frontier status refresh.
- `pass: false` feynman fixture: passed in prior review and covered by G8 frontier tests.

## Reporting Integration Results

- Evidence artifact index: passed. It indexes:
  - `decision/TF-001/decision_request.yaml`
  - `decision/TF-001/decision_result.yaml`
  - `feynman/TF-001/feynman_check.yaml`
  - `feynman/TF-001/feynman_result.yaml`
  - G8 phase labels are present for those artifacts.
- Delivery integration: passed. `delivery_packet.yaml` includes G8 artifacts and `g8_controls`; completed required results produced `status: completed`.
- GM report integration: passed. `gm_report.md` and `gm_report.yaml` disclose explicit Decision mode, explicit Feynman mode, deterministic controlled G8 mode, `real_runtime_used: false`, no automatic Decision Market, and no automatic Feynman executor.
- Awaiting Decision/Feynman status: passed. With required results missing, delivery and GM report status were `partial`, not `completed`, and controller tick did not auto-create artifacts.
- Reporting tests: passed. The two prior placeholder tests now assert completed delivery and GM report status, G8 controls, artifacts, and absence of awaiting markers.

## Idempotency Results

- Decision and Feynman core artifact hashes were stable across repeated explicit commands in prior review.
- `decision.completed` and `feynman.check.completed` were not duplicated in prior review.
- `decision status`, `decision result`, `feynman status`, and `feynman result` remain read-only.

## Boundary Check

- Branch diff does not include `.agentcomos/runs`, `uv.lock`, `reproduce*.sh`, or `reproduce*.log`.
- Branch diff does not include G0-G7 acceptance report status changes.
- Branch diff does not include G9+ implementation files.
- Boundary grep found historical docs/tests, the GM report disclosure line for disabled automatic Feynman executor, and existing G3/G4/G5 command builders. No new G8 real runtime path was found.
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

## Blocking Issues

None.

## Non-Blocking Notes

- `origin/main` currently tracks a partial `.agentcomos/runs/OI-TECHAI8-001` baseline (`run_status.yaml`, events/timeline, delivery/manifest) without `operating_intent.yaml`. Clean run setup was used for equivalent behavioral verification. No `.agentcomos/runs` diff is introduced by this G8 branch.
- `delivery_packet.yaml` still contains stale next-action wording: `Ready for Codex G6 review.` This is non-blocking because G8 artifacts, controls, and status semantics pass, but it should be cleaned up in a follow-up.

## Decision

G8 passed.

G9 Loop Execution may start after merge.

## Next Gate Unlock Status

Unlocked after G8 is merged to `main`.
