# G8 - Decision/Feynman Controlled Adoption Acceptance Report

## Status

failed

## Audit Metadata

- Audit time: 2026-06-09 14:18:08 CST
- Auditor: Codex
- Branch reviewed: `antigravity/g8-decision-feynman-controlled-adoption`
- Commit reviewed: `8f614ab6f615e1b1f8f94ced1cbfebac24a55f3e`
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
- G8 source and tests in the branch diff.

## Commands Executed

```bash
git fetch origin
git checkout antigravity/g8-decision-feynman-controlled-adoption
git pull origin antigravity/g8-decision-feynman-controlled-adoption
git status --short
git log --oneline -15
git diff --name-status origin/main...HEAD
grep -R "Loop Execution\|recursive task\|subagent\|Manual OS\|Worker Evolution\|Auto Versioner\|Decision Market executor\|Feynman executor\|automatic decision\|auto decision\|auto feynman" src tests scripts docs antigravity codex || true
grep -R "opencode serve\|opencode run\|run --attach\|hermes chat\|tmux new-session\|tmux send-keys\|discord\|Discord" src tests scripts || true
grep -R "pass\|assert True" tests/test_g8* || true
make compile
make test
make validate-examples
```

Manual acceptance commands were then executed for G1-G7 regression, G8 Decision/Feynman explicit mode, negative cases, Task Frontier blocking/unblocking, reporting integration, idempotency, and cleanup.

## Validation Results

- `make compile`: passed.
- `make test`: passed, `256 passed in 19.00s`.
- `make validate-examples`: passed.
- Empty G8 tests: passed. No empty `pass` or `assert True` placeholders found in `tests/test_g8*`.

## G1-G7 Regression Results

- G1 Controller: passed under equivalent CLI invocation. The restored `origin/main` tracked baseline contains a partial run, so `run create` returned idempotent `already exists`; status/recover did not crash.
- G2 Fake OpenCode: passed. Fake submit/status/collect completed for `OCJ-OI-TECHAI8-001-001`.
- G3 OpenCode availability: passed. Command did not crash and reported OpenCode available on this machine with version `unknown`.
- G4 Fake Hermes Worker: passed. Fake worker path still used tmux fake Hermes job semantics and was not rewritten into a G8 completion shortcut.
- G5 Hermes availability: passed. Command did not crash and reported `available: False`, `reason: hermes not found`.
- G6 Evidence / Delivery / GM Report regression: passed for pre-G8 G6 flow.
- G7 Program / Frontier: passed under a clean run setup. TF-001, TF-002, and TF-003 completed in order; fourth tick returned `no_ready_task`, not loop execution.

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

- `decision_required: true` without result: passed. TF-001 became `awaiting_decision`; `frontier next` returned no ready task; controller tick returned `no_ready_task`; no decision artifacts were auto-created.
- Decision result unblocking: passed. Explicit decision request unblocked TF-001 and the next controller tick completed it.
- `feynman_required: true` without result: passed. TF-002 became `awaiting_feynman`; controller tick did not execute it; no feynman artifacts were auto-created.
- Feynman result unblocking: passed. Explicit feynman check unblocked TF-002 and the next controller tick completed it.
- `pass: false` feynman fixture: passed. TF-002 stayed blocked with `failure_reason: feynman check failed`.

## Idempotency Results

- Decision and Feynman core artifact hashes were stable across repeated explicit commands.
- `decision.completed` event count stayed at 1 after repeat.
- `feynman.check.completed` event count stayed at 1 after repeat.
- `decision status`, `decision result`, `feynman status`, and `feynman result` were read-only.

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

1. Reporting integration is incomplete. `evidence_packet/artifact_index.yaml` does not index G8 artifacts such as `decision/TF-001/decision_request.yaml`, `decision/TF-001/decision_result.yaml`, `feynman/TF-001/feynman_check.yaml`, or `feynman/TF-001/feynman_result.yaml`.

2. Delivery integration is incomplete. `delivery_packet.yaml` does not include Decision/Feynman request/result artifacts and still reports a G6 next action (`Ready for Codex G6 review.`) in the G8 flow.

3. GM report integration is incomplete. `gm_report.md` and `gm_report.yaml` do not disclose explicit Decision adoption, explicit Feynman adoption, or deterministic controlled mode. They also do not make clear that no real multi-agent market or automatic trigger was used.

4. Awaiting Decision/Feynman gates do not affect reporting status. With TF-001 in `awaiting_decision`, both `delivery_packet.yaml` and `gm_report.yaml` still reported `status: completed`. G8 requires delivery/GM status not to be completed when required Decision/Feynman results are missing.

5. G8 tests do not cover the failing reporting requirements. There are G8 tests for basic Decision/Feynman generation and dependency resolution, but no G8 tests verifying artifact index integration, GM report disclosures, delivery packet integration, delivery/GM non-completed status while awaiting Decision/Feynman, controller tick no-auto-artifact behavior, or G8 boundary checks.

## Non-Blocking Notes

- `origin/main` currently tracks a partial `.agentcomos/runs/OI-TECHAI8-001` baseline (`run_status.yaml`, events/timeline, delivery/manifest) without `operating_intent.yaml`. The exact restore-then-create command sequence can therefore produce an idempotent existing run missing the intent file. Clean run setup was used for equivalent G7/G8 behavioral verification. No `.agentcomos/runs` diff is introduced by this G8 branch.

## Runtime Artifact Cleanup

Cleanup performed:

```bash
rm -rf .agentcomos/runs/OI-TECHAI8-001
rm -rf .agentcomos/runs/OI-MISSING-INTENT
git restore --source origin/main -- .agentcomos/runs
find . -maxdepth 1 \( -name 'uv.lock' -o -name 'reproduce*.sh' -o -name 'reproduce*.log' \) -delete
rm -rf .agentcomos/worker-runtime
```

Post-cleanup checks:

- `.agentcomos/runs` not present in `origin/main...HEAD` diff.
- `uv.lock` not present in `origin/main...HEAD` diff.
- `git status --short` was clean before this report update.

## Decision

G8 failed.

G9 Loop Execution remains locked. Antigravity must fix the G8 blocking issues in this branch before G8 can pass.

## Next Gate Unlock Status

Locked. G9 may not start until G8 is re-reviewed and this report is marked `passed`.
