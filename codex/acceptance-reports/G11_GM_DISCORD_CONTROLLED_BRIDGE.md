# G11 Acceptance Report

Status: failed

Audit time: 2026-06-10 03:36 Asia/Shanghai (2026-06-09T19:36:35Z)
Auditor: Codex
Branch reviewed: antigravity/g11-gm-discord-controlled-bridge
Commit reviewed: 6b2ea9dd97fafaee0e74bc85f55ef2e294fd752d

## Final Decision

G11 failed Codex acceptance.

G12 remains locked. Antigravity must fix the blocking issues in the G11 branch before G11 can be merged or used as the base for G12.

## Blocking Issues

1. Decision/Feynman Discord commands do not parse the required acceptance syntax.
   - Tested messages:
     - `decision result TF-002 approved`
     - `feynman result TF-002 pass`
   - Both parsed as `command_type: unknown` with `status: blocked`.
   - Required result: `decision_result` and `feynman_result` commands must require explicit confirmation, then execute through the G8 explicit result path.

2. Loop command artifacts do not preserve required parsed parameters.
   - `loop run OI-TECHAI8-001 max_ticks=3 fake` parsed as `loop_run_request`, but the generated `gm_command.yaml` did not record `max_ticks`, `fake`, or `real_runtime_used`.
   - Required result: command artifact must make bounded-loop and fake-runtime controls explicit and reviewable.

3. Confirmed loop execution failed the required acceptance path unless `loop_plan.yaml` was pre-created outside the Discord command.
   - After G11 setup (`run create`, `program build`, `frontier build`), confirmed execution of `loop run ... max_ticks=3 fake` returned `status: failed` with `loop_plan.yaml is missing`.
   - Required result: the G11 command path must either create/require the bounded loop plan as part of an explicit safe workflow or fail before being treated as an executable confirmed command. The acceptance command itself must pass.

4. Oversized loop requests are not rejected or clearly bounded.
   - `loop run OI-TECHAI8-001 max_ticks=999999 fake` was accepted after `loop plan` existed and produced a `completed` GM Discord command result: `Executed fake loop run with max_ticks=999999`.
   - Required result: oversized `max_ticks` must be rejected or capped and disclosed as bounded.

5. GM Discord audit is stale and incomplete.
   - `gm-discord audit` returns the existing audit file without regenerating or updating it.
   - After shell/manual/decision/feynman/loop commands, the audit still contained only the first status command.
   - Required result: audit must contain inbound, command, result, and safety boundary coverage for all G11 commands or explicitly regenerate idempotently when inputs change.

6. Repeated command execution is not idempotent for blocked commands.
   - Re-executing blocked decision/feynman commands appended duplicate `gm_discord.command.blocked` events.
   - Required result: repeated parse/execute should return `already_current` or otherwise avoid duplicate completed/blocked event spam.

7. Blocked shell command reason is too generic.
   - Dangerous message `run shell: sudo systemctl restart docker` was blocked and did not execute shell, but the result summary was only `Command is blocked for safety.`
   - Required result: blocked reason should disclose shell/unsafe/prohibited cause so Evidence/Delivery/GM report can explain why it was blocked.

8. GM report and delivery do not fully disclose G11 failures.
   - Delivery marked the oversized loop command as `completed`.
   - GM report asserted `loop_bounded: True` and did not disclose the blocked shell reason or oversized max_ticks acceptance.
   - Required result: reporting must not represent unsafe or out-of-policy G11 command outcomes as successful/compliant.

9. Changed file scope includes `tests/test_g6_evidence_packet.py`, which is outside the requested G11 allowed change list.
   - The diff removes the older `discord` guard from a G6 boundary test.
   - Required result: either justify this as an explicit G11 acceptance change in scope or move coverage into G11-specific tests without weakening earlier boundary tests.

## Verification Results

- make compile: passed.
- make test: passed, 375 tests passed.
- make validate-examples: passed.
- G1 Controller regression: passed using the project-local CLI equivalent (`PYTHONPATH=src ./.venv/bin/python3 -m agentcomos.cli`) because no global `agentcomos` executable was installed in this shell.
- G2 Fake OpenCode regression: passed.
- G3 OpenCode availability check: passed as non-blocking availability probe.
- G4 Fake Hermes Worker regression: passed.
- G5 Hermes availability check: passed as non-blocking availability probe (`hermes not found` reported, expected for availability probe).
- G6 Evidence / Delivery / GM regression: passed.
- G7 Program / Frontier regression: passed.
- G8 Decision/Feynman regression: passed; explicit mode still works through direct CLI.
- G9 Loop Execution regression: passed; bounded fake loop still works through direct CLI.
- G10 Manual OS regression: passed; immutable approval behavior still rejects changing approved to rejected.

## G11 Acceptance Matrix

- ingest requires fake: passed. Ingest without `--fake` was rejected with `G11 requires --fake`.
- ingest redacts inbound message: passed for status message safety fields; separate unit coverage also checks redaction.
- parse status command: passed. Parsed as read-only, low risk, no confirmation required.
- parse report command: not fully exercised manually in this audit run; unit test suite passed, but G11 remains failed on other blockers.
- parse manual-os command: passed. Parsed as `manual_os_approve`, confirmation required, medium risk, no real OS execution allowed.
- parse decision/feynman command: failed. Required acceptance syntax parsed as `unknown` and blocked.
- parse loop run command: failed. Parsed command type, but omitted required `max_ticks`, `fake`, and `real_runtime_used` fields.
- blocked shell command: partially passed. It was blocked and shell was not executed, but blocked reason did not disclose shell/unsafe/prohibited cause.
- execute read-only: passed. Status command completed with no shell execution and safety flags false.
- execute manual-os with explicit confirm: passed. Approval was produced through G10 Manual OS artifact after explicit confirmation.
- execute decision/feynman with explicit confirm: failed. Commands were blocked as `unknown`.
- execute loop run with max_ticks and fake: failed in the acceptance setup because `loop_plan.yaml` was missing; after manual `loop plan`, fake bounded execution worked for `max_ticks=3`.
- execute without confirm: passed. Manual OS and loop commands returned `requires_confirmation` before explicit confirmation.
- missing max_ticks: passed as fail-safe. Execution returned failed with `max_ticks must be provided and > 0`.
- real runtime loop request: passed as fail-safe. Execution returned failed with `loop run must be fake via Discord`.
- oversized max_ticks: failed. `max_ticks=999999 fake` completed instead of being rejected or clearly bounded.
- events appended: partially passed. Required G11 event types appeared, but duplicate blocked events were appended on repeated execution.
- timeline updated: passed for event reflection.
- evidence integration: passed. Artifact index included `discord_inbound_message`, `gm_command`, `gm_command_result`, and `gm_discord_audit`.
- delivery integration: failed. Delivery marked the oversized loop command completed and did not adequately distinguish out-of-policy completion.
- GM report integration: failed. Report disclosed fake adapter and static safety flags, but did not disclose key blocked/oversized command failures.
- idempotency/read-only: partially passed. `gm-discord status` and `audit` did not change hashes, but audit idempotency is stale/incomplete and repeated blocked execute appends duplicate events.

## Boundary Check

- real Discord connected: no.
- real Discord token required: no.
- real Discord message sent: no.
- shell executed: no.
- ssh executed: no.
- sudo executed: no.
- docker/systemctl executed: no.
- Manual OS bypassed: no evidence observed.
- Decision/Feynman bypassed: no evidence observed; however required Discord command integration failed to parse.
- unbounded loop: no infinite loop observed, but oversized `max_ticks=999999` was accepted as completed and must be rejected or capped.
- daemon/background service: no evidence observed.
- Worker Evolution: no implementation observed.
- Auto Versioner: no implementation observed.
- G12: no G12 implementation observed.

## Scope And Artifact Hygiene

- Runtime artifacts cleaned: passed.
- `.agentcomos/runs` not committed in G11 diff: passed.
- `uv.lock` not committed: passed.
- `.env` not committed: passed.
- Secrets clean: passed. Matches were documentation, placeholders, templates, or test negative strings only; no usable secret/key found.
- Real Discord implementation: not observed.
- Production daemon/scheduler service: not observed.

## Notes

- The worktree was clean after runtime cleanup before this acceptance report was edited.
- G11 remains failed. Real Discord deployment and production bridge remain locked until a future controlled phase.
