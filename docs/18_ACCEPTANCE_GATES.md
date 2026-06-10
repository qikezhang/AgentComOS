# Acceptance Gates
R3 Codex Review

## Codex Requirements
1. Code does not implement shell/docker adaptors (R4/R5).
2. Code handles duplicate message IDs safely.
3. Code does not leak Discord tokens to logs.
4. Unconfigured roles result in "blocked".
5. Test coverage contains negative idempotency and negative token load tests.
