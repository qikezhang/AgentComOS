# G3 — Real OpenCode Runtime Manager Acceptance Report

> 中文备注：本报告由 Codex 维护。Antigravity 提交实现后，Codex 必须执行本报告中的验收项，并将 Status 改为 `passed`、`failed` 或 `blocked`。

## Status

failed

## Audit Metadata

- Audit time: 2026-06-08 21:40:46 CST (+0800)
- Auditor: Codex
- Branch reviewed: `antigravity/g3-real-opencode-runtime-manager`
- Commit reviewed: `29a66eb8ae9cdc8092e23804bd9acdb67bb9cb4a`
- Working branch confirmed: `antigravity/g3-real-opencode-runtime-manager`
- Local OpenCode availability: `opencode not found`

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
git log --oneline -10
git diff --name-status origin/main...HEAD
grep -R "hermes chat\|tmux new-session\|tmux attach\|Loop Execution\|Manual OS\|Worker Evolution\|Auto Versioner\|Decision Market executor\|Feynman executor" src tests .agentcomos docs antigravity codex || true
grep -R "opencode serve\|opencode run\|run --attach" src tests || true
make compile
make test
make validate-examples
```

Manual G3 commands were also executed:

```bash
agentcomos opencode status
agentcomos opencode start
agentcomos opencode serve
agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
agentcomos opencode submit --run OI-TECHAI8-001 --phase plan --real
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
- `make test`: passed, `91 passed in 3.13s`.
- `make validate-examples`: passed.
- Tests did not require a real local `opencode` binary; local `opencode` was not found and the suite still passed.

## Real Runtime Status Check

- `agentcomos opencode status`: passed.
- Output clearly reported `available: False`, `reason: opencode not found`, `runtime: real_opencode`, `mode: real`, `version: unknown`.
- No crash occurred.
- No fake runtime artifacts were affected by status.
- `opencode_runtime_status.yaml` was not written by status alone, but was written after real submit.

Runtime status artifact after real submit:

- Path: `.agentcomos/runs/OI-TECHAI8-001/opencode_runtime_status.yaml`
- Fields included `runtime: real_opencode`, `available: false`, `mode: real`, `checked_at`, `reason: opencode not found`, and `version: unknown`.

## Real Submit Unavailable Behavior

With no local `opencode` binary:

- `agentcomos opencode submit --run OI-TECHAI8-001 --phase plan --real`: exited 0 and created a real OpenCode job artifact.
- Job path: `.agentcomos/runs/OI-TECHAI8-001/opencode_jobs/OCJ-OI-TECHAI8-001-001.yaml`.
- Job status was `unavailable`, not `completed`.
- Job recorded `runtime: real_opencode`, `phase: plan`, `created_by: controller`, `submitted_by: controller`, `fake_runtime: false`, `real_opencode_used: true`, `command`, `stdout_log`, and `stderr_log`.
- Real submit did not call Hermes and did not create tmux sessions.
- Real recover and real collect on the unavailable job did not crash.

Blocking detail: the unavailable job YAML did not include `failure_reason`, although the G3 manual acceptance requirement says `failure_reason` is required when a job is unavailable, blocked, or failed.

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

`git diff --name-status origin/main...HEAD` includes tracked run artifact deletions:

- `.agentcomos/runs/OI-TECHAI8-001/delivery_packet.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/events.jsonl`
- `.agentcomos/runs/OI-TECHAI8-001/evidence_packet/manifest.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/run_status.yaml`
- `.agentcomos/runs/OI-TECHAI8-001/timeline.yaml`

This violates the G3 instruction that the branch must not contain `.agentcomos/runs` runtime artifacts. The instruction explicitly states G3 must fail if `.agentcomos/runs` appears.

Other scope notes:

- `tests/test_opencode_g2_cli.py` is modified in the G3 branch. This appears related to preserving fake runtime behavior, but it is outside the narrow G3 test filenames listed by the user.
- No G0/G1/G2 acceptance report modification was present in the net diff against `origin/main`.

## Test Coverage Review

Direct or equivalent coverage found:

- `test_real_opencode_status_handles_missing_binary`
- `test_real_opencode_submit_requires_existing_run`
- `test_real_opencode_submit_missing_binary_creates_blocked_or_unavailable_job`
- `test_real_opencode_command_builder_uses_expected_serve_command`
- `test_real_opencode_command_builder_uses_run_attach_when_configured`
- G2 fake CLI tests still cover fake runtime behavior after G3.
- `test_real_collect_missing_job_fails`
- `test_real_collect_unavailable_job_is_read_only`

Coverage gaps relative to the requested list:

- No direct test named or clearly equivalent to `test_real_opencode_submit_does_not_fake_completion`.
- No direct test named or clearly equivalent to `test_make_tests_do_not_require_real_opencode`; manual review confirmed this but test coverage is missing.
- No direct test named or clearly equivalent to `test_real_runtime_does_not_call_hermes_or_tmux`; manual grep confirmed this but test coverage is missing.
- No direct test asserts `opencode_runtime_status.yaml` is written.
- No direct test asserts both stdout and stderr paths are recorded; current test only asserts stderr path.
- No direct test asserts missing-run real submit leaves no orphan artifacts.

## Runtime Artifacts Cleanup

Manual review artifacts were cleaned with:

```bash
find .agentcomos/runs -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true
```

After cleanup, `git status --short` was clean before this acceptance report was edited.

Important: cleanup removed local manual-run artifacts, but the branch diff still contains tracked `.agentcomos/runs/OI-TECHAI8-001/*` deletions relative to `origin/main`; that remains a branch-level blocking issue.

## Blocking Issues

1. G3 branch diff contains tracked `.agentcomos/runs/OI-TECHAI8-001/*` runtime artifact deletions. The user instruction says if `.agentcomos/runs` appears, G3 must fail.
2. Real unavailable job YAML is missing `failure_reason` even though G3 acceptance requires `failure_reason` when status is `unavailable`, `blocked`, or `failed`.
3. Required G3 test coverage is incomplete for no-fake-completion, no-real-opencode test dependency, no Hermes/tmux runtime calls, runtime status YAML writing, stdout/stderr path recording, and missing-run no-orphan-artifact behavior.

## Non-blocking Issues

- `opencode start` and `opencode serve` currently print the serve command rather than starting a process. This is acceptable only if G3 treats these commands as command-builder/controlled-start placeholders before full real serve lifecycle.
- The real runtime code sets available real jobs to `unavailable` as well; this was not exercised because local `opencode` was unavailable, but it should be reviewed before testing on a machine with real OpenCode.

## Rollback Note

Keep G4 locked. Antigravity should remove the tracked `.agentcomos/runs` diff, add the missing unavailable `failure_reason`, and add or strengthen the missing G3 tests before requesting another Codex review.

## Decision

G3 failed.

## Next Gate Unlock Status

G4 tmux Hermes Worker Pool Fake E2E remains locked until this report is marked `passed`.
