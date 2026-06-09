# G10 - Manual OS Controlled Adoption Acceptance Report

## Status

failed

## Summary
G10 failed Codex acceptance.

G11 remains locked. Antigravity must fix the blocking issues below in the G10 branch before merge. G11 GM/Discord Controlled Bridge must still be created later from latest `main` only after G10 passes and merges.

## Audit Metadata

- Audit time: 2026-06-10 02:09:57 CST
- Auditor: Codex
- Branch: `antigravity/g10-manual-os-controlled-adoption`
- Commit reviewed: `efa28f4841372210d389154e7d6a830d45b9dde7`
- PR: https://github.com/qikezhang/AgentComOS/pull/5

## Verification Results

- `make compile`: passed
- `make test`: passed, 325 tests passed
- `make validate-examples`: passed
- G1 Controller regression: passed with clean runtime directory and fake tick/recover
- G2 Fake OpenCode regression: passed
- G3 OpenCode availability: passed; local probe returned available
- G4 Fake Hermes Worker regression: passed
- G5 Hermes availability: passed; local probe reported `hermes not found` cleanly
- G6 Evidence / Delivery / GM regression: passed for prior-phase commands
- G7 Program / Frontier regression: passed
- G8 Decision/Feynman explicit regression: passed
- G9 bounded loop regression: passed

## G10 CLI Results

- `manual-os request`: passed; request file created with `manual_os_required: true`, `auto_execute: false`, human approval required, and all agent execution flags false
- `manual-os status`: passed; status read reported request/approval/result state
- `manual-os approve`: partially passed; approval file created with explicit approver and `auto_execute: false`
- `manual-os reject`: failed; reject can overwrite an existing approved request
- `manual-os result`: passed after re-approval; completed result requires prior approved status and records manual execution safety flags
- `manual-os audit`: passed for generated audit contents
- Missing run negative: passed; command failed
- Missing task negative: passed; command failed
- Approve without request negative: passed; command failed
- Approve without `--approved-by` negative: passed; command failed
- Result without approval negative: passed; command failed
- Result without `--executed-by` / required fields negative: passed; command failed

## Blocking Issues

1. Approval/rejection state is not immutable.

   `agentcomos manual-os reject --run OI-TECHAI8-001 --task TF-001 ...` succeeded after `TF-001` had already been approved and overwrote `manual_os_approval.yaml` from `status: approved` to `status: rejected`. Re-approval after rejection also succeeded. G10 requires reject-after-approve to fail or not overwrite, and controlled adoption must not allow terminal manual approval decisions to be silently flipped.

   Required fix: once `manual_os_approval.yaml` exists with `approved` or `rejected`, opposite-state commands must fail clearly or return already-current without changing the existing decision. Add regression coverage for approve-after-reject and reject-after-approve.

2. Loop does not stop on `awaiting_manual_os`.

   In isolated run `OI-G10-BLOCKED-MANUAL-OS`, `frontier status` correctly marked `TF-001` as `awaiting_manual_os` and `frontier next` returned `null`, but `loop run --max-ticks 3 --fake` produced `loop_status.status: completed` and `stop_reason: no_ready_task` instead of `status: blocked` and `stop_reason: awaiting_manual_os`.

   The loop trace recorded a normal `no_ready_task` tick, not a blocked Manual OS tick, and `controller_tick_called` was not recorded as `false`. Events also lacked `loop.tick.blocked_manual_os`.

   Required fix: loop blocker detection must treat tasks already in `awaiting_manual_os` as a Manual OS blocker, record a blocked tick with `blocked_on.type: manual_os`, set `controller_tick_called: false`, and stop with `awaiting_manual_os`.

3. Manual OS evidence integration is incomplete.

   On a run containing `manual_os_request.yaml`, `manual_os_approval.yaml`, `manual_os_result.yaml`, and `manual_os_audit.md`, `evidence_packet/artifact_index.yaml` did not index the Manual OS artifacts.

   Required fix: evidence artifact indexing must include `manual_os_request.yaml`, `manual_os_approval.yaml`, `manual_os_result.yaml`, and `manual_os_audit.md`.

4. Delivery integration omits the Manual OS audit artifact.

   `delivery_packet.yaml` included request, approval, and result artifacts, but omitted `manual_os_audit.md`.

   Required fix: delivery artifacts must include all Manual OS audit artifacts and disclose blocked `awaiting_manual_os` state without marking delivery completed when the run is blocked.

5. GM report safety disclosure is incomplete.

   `gm_report.md` and `gm_report.yaml` listed Manual OS task status, but did not disclose the required G10 safety controls: `auto_execute: false`, human approval required, human result report required, agent executed shell/ssh/sudo/docker/systemd false, and next action when awaiting Manual OS.

   Required fix: GM report must explicitly disclose Manual OS Controlled Adoption boundaries and must not imply autonomous OS operation.

6. Audit idempotency appends duplicate audit events.

   Re-running `manual-os audit` left file hashes unchanged, but appended another `manual_os.audit.generated` event. G10 requires repeated audit to be idempotent or already-current, without meaningless duplicate completed events.

   Required fix: repeated audit generation should avoid duplicate completed events when content is already current, or return an explicit already-current status.

## Boundary Check

- Agent executed shell: false in G10 Manual OS artifacts
- Agent executed ssh: false in G10 Manual OS artifacts
- Agent executed sudo: false in G10 Manual OS artifacts
- Agent executed docker/systemd: false in G10 Manual OS artifacts
- `subprocess` / `os.system` in `src/agentcomos/manual_os`: not found
- SSH / sudo / docker / systemctl execution in `src/agentcomos/manual_os`: not found
- Discord / GM bridge implementation in Manual OS runtime: not found
- Worker Evolution implementation in Manual OS runtime: not found
- Auto Versioner implementation in Manual OS runtime: not found
- Daemon/background service: not found in G10 Manual OS runtime
- Auto approval: not found, but approval state mutability is blocking
- Auto result: not found
- Secrets scan: no usable secret/key found; matches were documentation references only

## Cleanup Requirements

Runtime artifacts generated during audit were cleaned after the report update. `uv.lock`, `.env`, `.agentcomos/runs`, and runtime byproducts must not be committed.

## Final Decision

failed

Antigravity must fix the blocking issues in G10. G11 remains locked.
