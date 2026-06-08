# G3 — Real OpenCode Runtime Manager Acceptance Report

> 中文备注：本报告由 Codex 维护。Antigravity 提交实现后，Codex 必须执行本报告中的验收项，并将 Status 改为 `passed`、`failed` 或 `blocked`。

## Status

failed

## Supplemental Root Cause Note

2026-06-08 documentation clarification: the blocking failure is a runtime job routing bug, not an OpenCode availability bug.

Root cause:

```text
The implementation treated real_opencode_used as a job type routing field.
```

Correct classification:

```text
real_opencode_used is an execution result field only.
runtime and attempted_real_opencode are routing fields.
```

For an unavailable real OpenCode job:

```yaml
runtime: real_opencode
attempted_real_opencode: true
real_opencode_used: false
status: unavailable
```

`collect`, `status`, and `recover` must still route to the real OpenCode handler. `real_opencode_used: false` only means the real OpenCode command did not successfully execute; it does not make the job fake. See `docs/27_RUNTIME_JOB_ROUTING_RULES.md`.

## Audit Metadata

- Audit time: 2026-06-08 22:21:25 CST (+0800)
- Auditor: Codex
- Branch reviewed: `antigravity/g3-real-opencode-runtime-manager`
- Commit reviewed: `94e2e2e57c99081930451440f3a27402f1663165`
- Working branch confirmed: `antigravity/g3-real-opencode-runtime-manager`
- Local OpenCode availability: `opencode not found`
- Re-review context: Antigravity added `3527f56` and `94e2e2e` after the first failed G3 Codex review.

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
git fetch origin
git checkout antigravity/g3-real-opencode-runtime-manager
git pull origin antigravity/g3-real-opencode-runtime-manager
git status
git log --oneline -14
git diff --name-status origin/main...HEAD
grep -R "hermes chat\|tmux new-session\|tmux attach\|Loop Execution\|Manual OS\|Worker Evolution\|Auto Versioner\|Decision Market executor\|Feynman executor" src tests .agentcomos docs antigravity codex || true
grep -R "opencode serve\|opencode run\|run --attach" src tests || true
make compile
make test
make validate-examples
```

Manual G3 commands were also executed in sequence to avoid run-directory races:

```bash
agentcomos opencode status
agentcomos opencode start
agentcomos opencode serve
agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
agentcomos opencode submit --run OI-TECHAI8-001 --phase plan --real
agentcomos opencode status --job OCJ-OI-TECHAI8-001-001
agentcomos opencode recover --job OCJ-OI-TECHAI8-001-001
agentcomos opencode collect --job OCJ-OI-TECHAI8-001-001
agentcomos opencode submit --run OI-TECHAI8-001 --fake
agentcomos opencode status --job OCJ-OI-TECHAI8-001-001
agentcomos opencode collect --job OCJ-OI-TECHAI8-001-001
agentcomos opencode submit --run OI-DOES-NOT-EXIST --phase plan --real
agentcomos opencode status --job OCJ-REAL-DOES-NOT-EXIST
agentcomos opencode collect --job OCJ-REAL-DOES-NOT-EXIST
```

## Validation Results

- `make compile`: passed.
- `make test`: passed, `99 passed in 3.28s`.
- `make validate-examples`: passed.
- Tests did not require a real local `opencode` binary; local `opencode` was not found and the suite still passed.

## Real Runtime Status Check

- `agentcomos opencode status`: passed.
- Output clearly reported `available: False`, `reason: opencode not found`, `runtime: real_opencode`, `mode: real`, `version: unknown`.
- No crash occurred.
- No fake runtime artifacts were affected by status.

Runtime status artifact after real submit:

- Path: `.agentcomos/runs/OI-TECHAI8-001/opencode_runtime_status.yaml`.
- Fields included `runtime: real_opencode`, `available: false`, `mode: real`, `checked_at`, `reason: opencode not found`, and `version: unknown`.

## Real Submit Unavailable Behavior

With no local `opencode` binary:

- `agentcomos opencode submit --run OI-TECHAI8-001 --phase plan --real`: exited 0 and created a real OpenCode job artifact.
- Job path: `.agentcomos/runs/OI-TECHAI8-001/opencode_jobs/OCJ-OI-TECHAI8-001-001.yaml`.
- Job status was `unavailable`, not `completed`.
- Job recorded `runtime: real_opencode`, `phase: plan`, `created_by: controller`, `submitted_by: controller`, `fake_runtime: false`, `real_opencode_used: false`, `attempted_real_opencode: true`, `command`, `stdout_log`, `stderr_log`, and `failure_reason: opencode not found`.
- Real submit did not call Hermes and did not create tmux sessions.
- `agentcomos opencode status --job OCJ-OI-TECHAI8-001-001`: passed and printed the real job YAML.

Blocking detail: `agentcomos opencode collect --job OCJ-OI-TECHAI8-001-001` and `agentcomos opencode recover --job OCJ-OI-TECHAI8-001-001` failed for the unavailable real job. The job is real by `runtime: real_opencode` and `attempted_real_opencode: true`, but CLI routing checks only `real_opencode_used`; because unavailable jobs now correctly set `real_opencode_used: false`, the CLI falls through to fake collect/recover.

Root cause classification: `real_opencode_used` was used as a routing field, but it is only an execution result field. The routing fields for this job are `runtime: real_opencode` and `attempted_real_opencode: true`; both require the real OpenCode handler.

Observed failures:

- Collect exit code: 2, error says `delivery_packet.yaml is missing`, from the fake collect path.
- Recover exit code: 2, error says `Fake recover not implemented or required`.

## Fake Runtime Regression Check

G2 fake runtime was manually re-tested after G3 changes:

- `agentcomos opencode submit --run OI-TECHAI8-001 --fake`: passed.
- `agentcomos opencode status --job OCJ-OI-TECHAI8-001-001`: passed.
- `agentcomos opencode collect --job OCJ-OI-TECHAI8-001-001`: passed.
- Fake job contained `runtime: fake_opencode`, `fake_runtime: true`, `real_opencode_used: false`, and `status: completed`.
- Fake `opencode_project_plan.yaml` and `delivery_packet.yaml` existed.

Fake runtime preserved: yes.

## Negative Tests

- Missing run real submit: failed as expected with exit code 2.
- Missing run real submit did not create `opencode_jobs`, `opencode_logs`, or `opencode_outputs` under `.agentcomos/runs/OI-DOES-NOT-EXIST`.
- Missing job status: failed as expected with exit code 2.
- Missing job collect: failed as expected with exit code 2.

## Boundary Check

No runtime implementation of real Hermes, tmux Worker Pool, Loop Execution, Manual OS, Worker Evolution, Auto Versioner, Decision Market executor, or Feynman executor was found in the G3 runtime path.

Grep hits were reviewed:

- `src/agentcomos/cli.py` still contains inherited command skeleton printers for `tmux new-session` and `hermes chat -Q -q`; these print commands and are not called by G3 `opencode` runtime commands.
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

## Branch Scope Check

`git diff --name-status origin/main...HEAD` no longer includes `.agentcomos/runs/*` runtime artifact deletions. The previous tracked run artifact blocking issue is resolved.

Other scope notes:

- `tests/test_opencode_g2_cli.py` is modified in the G3 branch. This appears related to preserving fake runtime behavior after the CLI changed to require explicit `--fake` or `--real`.
- No G0/G1/G2 acceptance report modification was present in the net diff against `origin/main`.

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
- `test_branch_does_not_include_agentcomos_runs_artifacts`
- Missing-run real submit is covered by `test_real_opencode_submit_requires_existing_run`, but there is still no direct test asserting no orphan artifacts for that CLI path.

Coverage gap:

- No CLI-level regression test catches that unavailable real jobs with `attempted_real_opencode: true` but `real_opencode_used: false` are routed to fake collect/recover. The function-level `test_real_collect_unavailable_job_is_read_only` passes, but the actual CLI `agentcomos opencode collect --job ...` fails.

## Runtime Artifacts Cleanup

Manual review artifacts were cleaned with:

```bash
find .agentcomos/runs -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true
```

Tracked `.agentcomos/runs/OI-TECHAI8-001/*` files were restored after cleanup so the working tree no longer contains runtime artifact deletions. `git status --short` still shows an unrelated untracked `uv.lock`; it was not created by the G3 runtime checks and was not staged.

## Resolved Previous Blocking Issues

- Branch diff no longer contains tracked `.agentcomos/runs/OI-TECHAI8-001/*` runtime artifact deletions.
- Real unavailable job YAML now includes `failure_reason`.
- Most requested G3 tests were added or strengthened.

## Blocking Issues

1. CLI `agentcomos opencode collect --job <real_unavailable_job>` fails for unavailable real jobs because routing uses `real_opencode_used` instead of `runtime: real_opencode` or `attempted_real_opencode: true`.
2. CLI `agentcomos opencode recover --job <real_unavailable_job>` fails for the same routing reason.
3. There is no CLI-level test covering unavailable real job collect/recover routing, so the regression is not caught by `make test`.

Required regression coverage before G3 can pass:

- Unavailable real job with `real_opencode_used: false` still routes to real status handler.
- Unavailable real job with `attempted_real_opencode: true` still routes to real collect handler.
- `runtime` field has priority over `real_opencode_used`.
- Unknown runtime fails safely and does not default to fake.
- Fake job still routes to fake handler.

## Non-blocking Issues

- `opencode start` and `opencode serve` currently print the serve command rather than starting a process. This is acceptable only if G3 treats these commands as command-builder/controlled-start placeholders before full real serve lifecycle.
- The real runtime code sets available real jobs to `blocked`; this was not exercised because local `opencode` was unavailable, but it should be reviewed before testing on a machine with real OpenCode.

## Rollback Note

Keep G4 locked. Antigravity should route CLI collect/recover by `runtime: real_opencode` or `attempted_real_opencode: true`, add a CLI-level unavailable real job collect/recover regression test, and request another Codex review.

## Decision

G3 failed.

## Next Gate Unlock Status

G4 tmux Hermes Worker Pool Fake E2E remains locked until this report is marked `passed`.
