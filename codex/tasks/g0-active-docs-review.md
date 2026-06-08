# Codex Task — G0 Active Docs Review

> 中文备注：这是 v2.8.6 的首个 Codex 任务。目标是先把文档边界审清楚，再允许 Antigravity 开始 G1 Controller 编码。

## Goal

Codex must verify active vs archived documents and produce `codex/acceptance-reports/G0_CONTRACT_BASELINE.md`.

## Inputs

- `docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md`
- `RELEASE_MANIFEST.md`
- `AGENTS.md`
- `docs/17_PHASED_DELIVERY_PLAN.md`
- `docs/18_ACCEPTANCE_GATES.md`
- `docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md`

## Required Checks

1. Active docs are v2.8.6 consistent.
2. Historical docs are marked archived.
3. v2.8 product spec has implementation overlay note.
4. Decision/Feynman strategy is Explicit -> Assisted -> Industrial Auto.
5. G0-G11 acceptance reports exist.
6. Antigravity must not use archived docs as active implementation policy.

## Required Commands

```bash
make compile
make test
make validate-examples
```

## Required Output

Update:

```text
codex/acceptance-reports/G0_CONTRACT_BASELINE.md
```

Status must become `passed`, `failed`, or `blocked`.
