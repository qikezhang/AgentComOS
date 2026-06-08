# G3 — Real OpenCode Runtime Manager Acceptance Report

> 中文备注：本报告由 Codex 维护。Antigravity 提交实现后，Codex 必须执行本报告中的验收项，并将 Status 改为 `passed`、`failed` 或 `blocked`。

## Status

passed

## Audit Metadata

- Audit time: 2026-06-08 22:44:25 CST (+0800)
- Auditor: Codex
- Branch reviewed: `antigravity/g3-real-opencode-runtime-manager`
- Commit reviewed: `ff2723afcd23fbe423a7282721c8931cfdbcfd77`
- Working branch confirmed: `antigravity/g3-real-opencode-runtime-manager`
- Local OpenCode availability: `opencode not found`
- Re-review context: this review includes `1ae91fe` (`fix(opencode): route real unavailable jobs by runtime`) and `ff2723a` (`docs: clarify runtime job routing rules`).

G3 passed.
G4 tmux Hermes Worker Pool Fake E2E may start after merge.

## Inputs Reviewed

- `AGENTS.md`
- `docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md`
- `docs/17_PHASED_DELIVERY_PLAN.md`
- `docs/18_ACCEPTANCE_GATES.md`
- `docs/modules/02_opencode_runtime_manager.md`
- `antigravity/tasks/phase-3-real-opencode-runtime-manager.md`
- `codex/acceptance-reports/G3_REAL_OPENCODE_RUNTIME_MANAGER.md`

## Commands Executed

```bash
git branch --show-current
git rev-parse HEAD
git status --short
git log --oneline -10
git diff --name-status origin/main...HEAD
grep -R "hermes chat\|tmux new-session\|tmux attach\|Loop Execution\|Manual OS\|Worker Evolution\|Auto Versioner\|Decision Market executor\|Feynman executor" src tests .agentcomos docs antigravity codex || true
grep -R "opencode serve\|opencode run\|run --attach" src tests || true
make compile
make test
make validate-examples
which opencode || true
```

Manual G3 commands were executed in sequence:

```bash
agentcomos opencode status
agentcomos opencode start
agentcomos opencode serve
rm -rf .agentcomos/runs/OI-TECHAI8-001
agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
agentcomos opencode submit --run OI-TECHAI8-001 --phase plan --real
agentcomos opencode status --job OCJ-OI-TECHAI8-001-001
agentcomos opencode recover --job OCJ-OI-TECHAI8-001-001
agentcomos opencode collect --job OCJ-OI-TECHAI8-001-001
rm -rf .agentcomos/runs/OI-TECHAI8-001
agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
agentcomos opencode submit --run OI-TECHAI8-001 --fake
agentcomos opencode status --job OCJ-OI-TECHAI8-001-001
agentcomos opencode collect --job OCJ-OI-TECHAI8-001-001
agentcomos opencode submit --run OI-DOES-NOT-EXIST --phase plan --real
agentcomos opencode status --job OCJ-REAL-DOES-NOT-EXIST
agentcomos opencode collect --job OCJ-REAL-DOES-NOT-EXIST
```

## Validation Results

- `make compile`: passed.
- `make test`: passed, `104 passed in 1.91s`.
- `make validate-examples`: passed.
- Tests did not require a real local `opencode` binary; local `opencode` was not found and the suite still passed.

## Real Runtime Status Check

- `agentcomos opencode status`: passed.
- Output reported `available: False`, `reason: opencode not found`, `runtime: real_opencode`, `mode: real`, and `version: unknown`.
- No crash occurred.
- No fake runtime artifacts were affected.
- `agentcomos opencode start` and `agentcomos opencode serve` printed the controlled command `opencode serve --hostname 127.0.0.1 --port 4096`; no server process was launched during review.

Runtime status artifact after real submit:

- Path: `.agentcomos/runs/OI-TECHAI8-001/opencode_runtime_status.yaml`.
- Fields included `runtime: real_opencode`, `available: false`, `mode: real`, `checked_at`, `reason: opencode not found`, and `version: unknown`.

## Real Submit Unavailable Behavior

With no local `opencode` binary:

- `agentcomos opencode submit --run OI-TECHAI8-001 --phase plan --real`: exited 0 and created `.agentcomos/runs/OI-TECHAI8-001/opencode_jobs/OCJ-OI-TECHAI8-001-001.yaml`.
- Job status was `unavailable`, not `completed`.
- Job recorded `runtime: real_opencode`, `phase: plan`, `created_by: controller`, `submitted_by: controller`, `fake_runtime: false`, `real_opencode_used: false`, `attempted_real_opencode: true`, `command`, `stdout_log`, `stderr_log`, and `failure_reason: opencode not found`.
- Real submit did not call Hermes and did not create tmux sessions.
- `agentcomos opencode status --job OCJ-OI-TECHAI8-001-001`: passed and printed the real job YAML.
- `agentcomos opencode recover --job OCJ-OI-TECHAI8-001-001`: passed and reported the real job recovered.
- `agentcomos opencode collect --job OCJ-OI-TECHAI8-001-001`: passed and reported the real job collected or in read-only mode.

The previous routing blocker is resolved: unavailable real jobs now route by `runtime: real_opencode` / `attempted_real_opencode: true`, not by `real_opencode_used`.

## Fake Runtime Regression Check

G2 fake runtime was manually re-tested after G3 changes:

- `agentcomos opencode submit --run OI-TECHAI8-001 --fake`: passed.
- `agentcomos opencode status --job OCJ-OI-TECHAI8-001-001`: passed.
- `agentcomos opencode collect --job OCJ-OI-TECHAI8-001-001`: passed.
- Fake job contained `runtime: fake_opencode`, `fake_runtime: true`, `real_opencode_used: false`, `real_hermes_used: false`, and `status: completed`.
- Fake `opencode_project_plan.yaml` and `delivery_packet.yaml` existed.

Fake runtime preserved: yes.

## Negative Tests

- Missing run real submit failed as expected with exit code 2.
- Missing run real submit did not create `opencode_jobs`, `opencode_logs`, or `opencode_outputs` under `.agentcomos/runs/OI-DOES-NOT-EXIST`.
- Missing job status failed as expected with exit code 2.
- Missing job collect failed as expected with exit code 2.

## Boundary Check

No runtime implementation of real Hermes, tmux Worker Pool, Loop Execution, Manual OS, Worker Evolution, Auto Versioner, Decision Market executor, or Feynman executor was found in the G3 runtime path.

Grep hits were reviewed:

- `src/agentcomos/cli.py` contains inherited command skeleton printers for `tmux new-session` and `hermes chat -Q -q`; these print commands and are not called by G3 `opencode` runtime commands.
- Documentation and `.agentcomos/manual-os/*` policy/manual files contain Loop/Manual/Worker Evolution/Auto Versioner references; classified as documentation/config only.
- `src/agentcomos/opencode/commands.py` builds `opencode serve` and `opencode run --attach` command strings.
- G3 real OpenCode use is explicit via `--real`; fake path remains separate.

Confirmations:

- Real OpenCode controlled explicit only: yes.
- Fake runtime preserved: yes.
- Real Hermes integration: no.
- tmux Worker Pool: no.
- Loop Execution: no.
- Manual OS runtime implementation: no.
- Worker Evolution runtime implementation: no.
- Auto Versioner runtime implementation: no.
- Decision Market executor: no.
- Feynman executor: no.
- `make test` depends on real OpenCode: no.

## Branch Scope Check

`git diff --name-status origin/main...HEAD` contains G3 runtime code, G3 tests, G3 task documentation, G3 routing documentation, and this G3 acceptance report. It does not contain `.agentcomos/runs/*` runtime artifacts, unrelated deletions, or G0/G1/G2 acceptance report modifications.

Scope notes:

- `tests/test_opencode_g2_cli.py` is modified to preserve fake runtime behavior after the CLI changed to require explicit `--fake` or `--real`.
- G3 routing documentation changes are treated as necessary G3 documentation and do not modify the v2.8 product boundary.

## Test Coverage Review

Direct or equivalent coverage found:

- `test_real_opencode_status_handles_missing_binary`
- `test_real_opencode_submit_requires_existing_run`
- `test_real_opencode_submit_missing_binary_creates_blocked_or_unavailable_job`
- `test_real_unavailable_job_has_failure_reason`
- `test_real_opencode_submit_does_not_fake_completion`
- `test_real_opencode_command_builder_uses_expected_serve_command`
- `test_real_opencode_command_builder_uses_run_attach_when_configured`
- `test_fake_runtime_still_passes_after_g3`
- `test_make_tests_do_not_require_real_opencode`
- `test_real_runtime_does_not_call_hermes_or_tmux`
- `test_runtime_status_yaml_is_written`
- `test_real_submit_records_stdout_stderr_paths`
- `test_real_collect_missing_job_fails`
- `test_real_collect_unavailable_job_is_read_only`
- `test_real_opencode_submit_missing_run_fails_without_orphan_artifacts`
- `test_unavailable_real_job_routes_to_real_status_even_when_real_opencode_used_false`
- `test_unavailable_real_job_routes_to_real_collect_even_when_real_opencode_used_false`
- `test_runtime_field_has_priority_over_real_opencode_used`
- `test_fake_job_still_routes_to_fake_path`
- `test_unknown_job_runtime_fails_safely`
- `test_branch_does_not_include_agentcomos_runs_artifacts`

The requested scenarios are covered directly or by equivalent tests.

## Runtime Artifacts Cleanup

Manual review artifacts were cleaned with:

```bash
find .agentcomos/runs -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true
```

Tracked `.agentcomos/runs/OI-TECHAI8-001/*` files were restored after cleanup. `git status --short` showed no `.agentcomos/runs` runtime artifacts; an unrelated untracked `uv.lock` remains unstaged.

## Resolved Previous Blocking Issues

- Branch diff no longer contains tracked `.agentcomos/runs/OI-TECHAI8-001/*` runtime artifact deletions.
- Real unavailable job YAML now includes `failure_reason`.
- CLI status, collect, and recover now route unavailable real jobs to the real OpenCode handler.
- CLI-level routing regression tests were added.

## Blocking Issues

None.

## Non-blocking Notes

- `opencode start` and `opencode serve` currently print the serve command rather than starting a process. This is acceptable for this gate as a controlled command-builder surface; full process lifecycle should be revisited before production real OpenCode operation.
- The local review environment did not have real `opencode`; unavailable/blocked behavior was fully exercised, but successful real execution on a machine with OpenCode installed remains a later smoke-test concern.

## Rollback Note

If regressions appear before merge, revert the G3 branch changes and return to the G2 fake runtime baseline. G4 must start only from a merged G3 commit that preserves fake runtime and explicit real runtime boundaries.

## Decision

G3 passed.

## Next Gate Unlock Status

G4 tmux Hermes Worker Pool Fake E2E may start after merge.
