# R3 Real Discord Bot Adapter

Status: pending

Branch: antigravity/r3-real-discord-bot-adapter
Commit: $(git rev-parse HEAD)
Owner: Antigravity
Reviewer: Codex

## Scope

- Real Discord Bot adapter: Yes
- Token loading: Yes
- Missing token unavailable: Yes
- Token redaction: Yes
- Guild allowlist: Yes
- Channel allowlist: Yes
- User allowlist: Yes
- Role allowlist: Yes
- Denied role override: Yes
- Permission result artifact: Yes
- Inbound artifact: Yes
- GM command artifact: Yes
- Outbound artifact: Yes
- Audit artifact: Yes
- Read-only command: Yes
- Controlled command request: Yes
- Duplicate message idempotency: Yes
- Secret request blocked: Yes
- Arbitrary command blocked: Yes

## Out of scope confirmation

- Controlled Executor: Not implemented
- shell adapter: Not implemented
- ssh adapter: Not implemented
- sudo adapter: Not implemented
- docker adapter: Not implemented
- systemctl adapter: Not implemented
- arbitrary command execution: Not implemented

## Validation

- make compile: Passed
- make test: Passed
- make validate-examples: Passed (schemas unchanged, R2 pass retained)
- targeted R3 tests: Passed
- R2 regression tests: Passed
- healthcheck: Passed
- docker compose config: Passed
- docker build/run: Passed via CI/regression check

## Hygiene

- .agentcomos/runs: Clean
- .env: Not committed
- uv.lock: Clean
- secrets: Clean

## Notes

Ready for Codex R3 review.
