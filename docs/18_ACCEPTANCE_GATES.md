# AgentComOS v2.8.6 Acceptance Gates

> 中文备注：本文件把阶段计划转成可执行验收卡。Codex 依据本文件审计，Antigravity 依据本文件提交 evidence。

## Gate Template

每个 Gate 必须包含：

```text
Goal
Inputs
Commands
Required outputs
Positive tests
Negative tests
Evidence artifacts
Codex acceptance report
Antigravity implementation report
Rollback note
Next gate unlock condition
```

## G0 — Contract Baseline

Goal：工程契约包一致、可测试。

Commands：

```bash
make compile
make test
make validate-examples
```

Evidence：

```text
pytest output
validate-examples output
release manifest
```

## G1 — Controller Minimum State Machine

Inputs：

```text
examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
schemas/run_status.schema.json
schemas/event_record.schema.json
```

Commands：

```bash
agentcomos run create --intent examples/techai8/run/OI-TECHAI8-001/operating_intent.yaml
agentcomos controller tick --run <run_id> --fake
agentcomos run status --run <run_id>
agentcomos controller recover --run <run_id>
```

Required outputs：

```text
.agentcomos/runs/<run_id>/run_status.yaml
.agentcomos/runs/<run_id>/events.jsonl
.agentcomos/runs/<run_id>/timeline.yaml
```

Positive tests：

```text
test_run_create_generates_status
test_tick_advances_state
test_tick_is_idempotent
test_recover_restores_state
```

Negative tests：

```text
duplicate run create cannot overwrite
missing operating_intent fails
invalid transition fails
```

## G2 — Fake OpenCode Runtime

Commands：

```bash
agentcomos opencode submit --run <run_id> --fake
agentcomos opencode collect --job <job_id>
```

Required outputs：

```text
opencode_job.yaml
opencode_project_plan.yaml
delivery_packet.yaml
stdout.jsonl
```

Negative tests：

```text
collect unknown job fails
completed job without delivery_packet fails
```

## G3 — Real OpenCode Runtime Manager

Commands：

```bash
agentcomos opencode start
agentcomos opencode status
agentcomos opencode submit --run <run_id> --phase plan
agentcomos opencode collect --job <job_id>
agentcomos opencode recover
```

Required outputs：

```text
opencode_job.yaml
opencode_session_ledger.yaml
stdout.jsonl
stderr.log
session_export.json
```

Negative tests：

```text
server unavailable -> job blocked/stalled
hard timeout -> failed
no session ledger -> fail
```

Runtime routing acceptance：

```text
unavailable real job with real_opencode_used=false must still route to real status handler
unavailable real job with attempted_real_opencode=true must still route to real collect handler
runtime field has priority over real_opencode_used
unknown runtime must fail safely and must not default to fake
fake job must still route to fake handler
```

Routing rule reference：`docs/27_RUNTIME_JOB_ROUTING_RULES.md`

## G4 — tmux Hermes Worker Pool Fake E2E

Commands：

```bash
agentcomos worker start --fake --invocation <HWI.yaml>
agentcomos worker status --job <job_id>
agentcomos worker collect --job <job_id>
agentcomos worker list --run <run_id>
agentcomos worker kill --job <job_id>
agentcomos worker recover --run <run_id>
```

Required outputs：

```text
worker_jobs/<worker_job_id>.yaml
worker_outputs/<task_id>/DONE.md
worker_outputs/<task_id>/result.yaml
worker_outputs/<task_id>/reasoning_summary.md
tmux log
events.jsonl worker events
timeline.yaml worker events
```

Positive tests：

```text
fake worker writes DONE.md/result.yaml/reasoning_summary.md
worker start writes worker_job.yaml
tmux command runs fake_hermes_worker.py only
repeated worker start is idempotent
repeated collect is idempotent
recover reads existing jobs and outputs
```

Negative tests：

```text
missing DONE.md -> not completed
output_dir outside run -> fail
unknown worker_id -> fail
missing invocation -> fail without orphan job
tmux unavailable -> clear unavailable/blocked state, not completed
real Hermes command usage -> fail
```

Rollback note：

```text
Remove G4 worker package, worker CLI commands, fake worker script, tests, and docs.
Do not rewrite operating data history in .agentcomos/runs.
```

## G5 — Real Hermes Worker Runtime

Required proof：

```text
command uses tmux + hermes chat -Q -q
no custom worker daemon exists
required outputs collected
failure_report recorded on failure
```

## G6 — Evidence / Delivery / GM Report

Required outputs：

```text
evidence_packet/
delivery_packet.yaml
user_report_packet.yaml
gm_report.md
```

Negative tests：

```text
GM report directly references raw worker output -> fail
missing risk summary -> fail
missing next action -> fail
```

## G7 — Simple Operating Program

Goal：跑通最小长期运营节奏，但不启用复杂 Loop。

Inputs：

```text
operating_program.yaml
daily_operating_packet.yaml
four_hour_operating_packet.yaml
hourly_health_snapshot.yaml
```

Commands：

```bash
agentcomos operating create --template examples/techai8/operating_program.yaml
agentcomos scheduler tick --hourly --fake
agentcomos scheduler tick --daily --fake
```

Required outputs：

```text
.agentcomos/runs/<run_id>/hourly_health_snapshot.yaml
.agentcomos/runs/<run_id>/daily_operating_packet.yaml
.agentcomos/runs/<run_id>/user_report_packet.yaml
```

Negative tests：

```text
operating program without metric -> fail
daily packet without next_actions -> fail
hourly check cannot mutate production state -> fail
```

Codex report：`codex/acceptance-reports/G7_SIMPLE_OPERATING_PROGRAM.md`

## G8 — Decision/Feynman Controlled Adoption

Goal：实现 development_explicit → transition_assisted → industrial_auto 三阶段策略。

Commands：

```bash
agentcomos decision evaluate --run <run_id> --stage development_explicit
agentcomos feynman evaluate --run <run_id> --stage development_explicit
```

Required outputs：

```text
decision_adoption_decision.yaml
feynman_adoption_decision.yaml
```

Positive tests：

```text
user explicit request enables mini decision
task policy required enables feynman lite
high risk release forces review gate
industrial_auto can system-enable decision/feynman
```

Negative tests：

```text
development_explicit cannot silently system_auto
transition_assisted requires GM/user confirmation
industrial_auto without budget policy -> fail
```

Codex report：`codex/acceptance-reports/G8_DECISION_FEYNMAN_CONTROLLED_ADOPTION.md`

## G9 — Loop Execution + Task Frontier

Goal：批量循环任务可控执行。

Commands：

```bash
agentcomos loop create --request <loop_execution_request.yaml>
agentcomos loop tick --loop <loop_id> --fake
agentcomos loop status --loop <loop_id>
```

Required outputs：

```text
loop_batch.yaml
batch_result.yaml
next_frontier_candidates.yaml
loop_status.yaml
```

Negative tests：

```text
missing budget -> fail
missing stop_conditions -> fail
max_parallel_workers > 3 -> fail
loop task without worker invocation -> fail
```

Codex report：`codex/acceptance-reports/G9_LOOP_EXECUTION_TASK_FRONTIER.md`

## G10 — Manual OS / Worker Evolution / Auto Versioner

Goal：知识资产、自进化和版本治理闭环。

Required examples：

```text
examples/manual-os/growth-manual-update/
examples/worker-evolution/patch-approved/
examples/versioning/medium-risk-release/
```

Required outputs：

```text
manual_update_proposal.yaml
manual_release_decision.yaml
worker_evaluation.yaml
failure_attribution.yaml
ratchet_decision.yaml
change_set.yaml
rollback_target.yaml
version_record.yaml
```

Negative tests：

```text
GM directly modifies manual -> fail
Worker patch without ratchet -> fail
medium/high risk release without rollback target -> fail
raw operating data in GitTree release path -> fail
```

Codex report：`codex/acceptance-reports/G10_MANUAL_WORKER_EVOLUTION_AUTO_VERSIONER.md`

## G11 — Industrial Auto Governance

Goal：系统可自动判断何时启用 Decision / Feynman / Loop / Evolution，并具备商业化部署审计能力。

Required proof：

```text
commercial deployment readiness checklist
backup/restore rehearsal
rollback rehearsal
secrets audit
cost budget ledger
GM approval flow
production healthcheck
industrial_auto decision logs
```

Negative tests：

```text
auto decision without event log -> fail
auto feynman without budget -> fail
production deploy without rollback rehearsal -> fail
credential request without approval flow -> fail
```

Codex report：`codex/acceptance-reports/G11_INDUSTRIAL_AUTO_GOVERNANCE.md`

## Gate Reporting Rule

Codex 必须为 G0-G11 全部维护验收报告。G7-G11 可以在当前阶段保持 pending，但进入对应 Phase 前必须补齐细则，合并前必须执行并更新状态。详见 `docs/25_PHASE_ACCEPTANCE_REPORTING.md`。
