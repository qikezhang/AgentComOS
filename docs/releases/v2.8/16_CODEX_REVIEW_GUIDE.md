# 16 Codex Review Guide

Codex must review that documentation and implementation accurately distinguish:

- current G11 implementation
- v2.8 final target
- future post-v2.8 items

## Required checks

- No fake bridge is described as real Discord.
- No current G11 code is described as supporting shell execution.
- Docker production target is documented as R2.
- Real Discord Bot target is documented as R3.
- Controlled Executor target is documented as R4.
- Operation Adapters target are documented as R5.
- CI/incident/retention hardening is documented for release readiness.
- Arbitrary command execution is never allowed.
- No secret or real token appears in docs/testdata/templates.
