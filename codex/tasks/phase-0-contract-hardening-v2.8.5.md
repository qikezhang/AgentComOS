# Codex Task: Phase 0 v2.8.5 Contract Review

## Goal

Verify that AgentComOS v2.8.5 is a consistent controlled-to-industrial engineering contract.

## Inputs

```text
README.md
RELEASE_MANIFEST.md
docs/04_DEVELOPMENT_ROADMAP.md
docs/05_ACCEPTANCE_MATRIX.md
docs/15_CODEX_ANTIGRAVITY_COLLABORATION.md
docs/16_CONTROLLER_IMPLEMENTATION_SPEC.md
docs/17_PHASED_DELIVERY_PLAN.md
docs/18_ACCEPTANCE_GATES.md
docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md
```

## Checks

- No stale v2.8.4 release positioning in active docs.
- Decision / Feynman adoption is staged: development_explicit -> transition_assisted -> industrial_auto.
- Controller is the first implementation priority.
- Acceptance gates are actionable.
- Codex / Antigravity boundaries are explicit.
- Runtime profile says host-systemd MVP, docker-tmux experimental.

## Required command

```bash
make compile
make test
make validate-examples
```

## Output

Use `docs/templates/codex_review_report.md`.
