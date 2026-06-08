# AGENTS.md — AgentComOS v2.8.6 Engineering Rules

## Non-negotiable architecture rules

1. Users communicate with GM, not OpenCode or Workers.
2. GM never calls Workers, never creates Worker Invocation, never starts tmux, never reads raw Worker outputs as final truth.
3. OpenCode is the only actor that can request Workers.
4. Controller executes Worker Invocation, manages runtime state, and does not make cognitive decisions.
5. Hermes Worker is a tmux-launched Hermes CLI instance, not a new custom worker program.
6. Decision Market and Feynman adoption is staged:
   - development_explicit: explicit user/task/high-risk only.
   - transition_assisted: system suggests, GM/user/task confirms.
   - industrial_auto: system can automatically decide based on policy.
7. Every non-trivial run must produce an Evidence Packet or Evidence Lite according to phase.
8. Environment facts must be probed; agents must not guess versions, commands, paths, timezone, or runtime capabilities.
9. GitTree / Auto Versioner govern platform, agent, worker, manual, skill, project code, and policy versions. Raw operating data is not a GitTree release object.
10. Controller is P0 and must be implemented before broad runtime/worker/loop functionality.

## Codex responsibilities

Codex owns:

- project management and phase gates
- product and engineering specs
- protocol and schema reviews
- tests, negative tests, acceptance matrix
- documentation consistency checks
- PR review tasks and release manifest
- commercial deployment audit gates

Codex should not directly implement production runtime code unless it is test/validator support.

## Antigravity responsibilities

Antigravity owns:

- code implementation
- Controller runtime
- OpenCode runtime manager
- tmux Hermes worker pool
- Docker / Contabo deployment
- fake runtime and real runtime integration
- observability and runbooks

Antigravity must not lower acceptance gates or bypass Codex review.

## Required acceptance before implementation changes

For every feature, include:

- schema or contract
- example input and output
- unit test, validation test, or fake E2E
- docs update
- acceptance criterion in `docs/18_ACCEPTANCE_GATES.md`
- evidence artifact or log sample
- rollback note when runtime or deployment changes are involved

## Phase discipline

Do not jump to full implementation. The required order is:

1. Controller state machine
2. fake OpenCode runtime
3. real OpenCode runtime
4. fake tmux Hermes worker
5. real Hermes worker
6. Evidence / Delivery / GM report
7. Operating Program
8. optional/assisted Decision and Feynman
9. Loop Execution
10. Manual OS / Worker Evolution / Auto Versioner
11. industrial auto governance
