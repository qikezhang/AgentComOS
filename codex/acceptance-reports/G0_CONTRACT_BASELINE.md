# G0 — Contract Baseline Acceptance Report

> 中文备注：本报告由 Codex 维护。Antigravity 提交实现后，Codex 必须执行本报告中的验收项，并将 Status 改为 `passed`、`failed` 或 `blocked`。

## Status

passed

## Scope

Codex active docs review and engineering contract baseline.

## Inputs Reviewed

- `README.md`
- `RELEASE_MANIFEST.md`
- `AGENTS.md`
- `docs/00_PRODUCT_SPEC_V2_8.md`
- `docs/11_ENGINEERING_CONTRACT_V2_8_3.md`
- `docs/13_CONTRACT_HARDENING_V2_8_4.md`
- `docs/17_PHASED_DELIVERY_PLAN.md`
- `docs/18_ACCEPTANCE_GATES.md`
- `docs/19_DECISION_FEYNMAN_ADOPTION_POLICY.md`
- `docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md`
- `docs/25_PHASE_ACCEPTANCE_REPORTING.md`

Environment facts probed:

- Workspace: `/Volumes/xbb-home/github/AgentComOS`
- Git branch: `codex/g0-contract-fix`
- Git commit: `7149958`
- Probe time: `2026-06-08 15:09:40 CST +0800`
- Python: `Python 3.14.3`

## Commands Executed

```bash
make compile             # pass
make test                # pass, 44 passed in 1.75s
make validate-examples   # pass, Run validation passed
```

## Required Artifacts Checked

- Active document policy exists: `docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md`
- G0 task exists: `codex/tasks/g0-active-docs-review.md`
- G0-G11 acceptance reports exist under `codex/acceptance-reports/`
- Historical contract stubs exist:
  - `docs/11_ENGINEERING_CONTRACT_V2_8_3.md`
  - `docs/13_CONTRACT_HARDENING_V2_8_4.md`
- Archived historical copies exist:
  - `docs/archive/11_ENGINEERING_CONTRACT_V2_8_3.md`
  - `docs/archive/13_CONTRACT_HARDENING_V2_8_4.md`

## Positive Tests

- `README.md`, `RELEASE_MANIFEST.md`, and `docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md` identify the starter as AgentComOS v2.8.6.
- `docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md` explicitly lists active implementation documents.
- `docs/24_ACTIVE_DOCUMENTS_AND_ARCHIVE_POLICY.md` marks `docs/11_ENGINEERING_CONTRACT_V2_8_3.md` and `docs/13_CONTRACT_HARDENING_V2_8_4.md` as historical references that must not drive current implementation.
- `docs/11_ENGINEERING_CONTRACT_V2_8_3.md` and `docs/13_CONTRACT_HARDENING_V2_8_4.md` are archived-reference stubs pointing to `docs/archive/`.
- `docs/00_PRODUCT_SPEC_V2_8.md` states it is the complete v2.8 product target baseline and that v2.8.6 development strategy follows the current active docs.
- Decision/Feynman policy is consistently staged as `development_explicit` -> `transition_assisted` -> `industrial_auto`.
- `AGENTS.md` now identifies the current engineering rules as AgentComOS v2.8.6.
- `README.md` and `RELEASE_MANIFEST.md` now record the current validation result of `make test` as `44 passed`.
- Required validation commands all pass.

## Negative Tests

- Version consistency re-check found `AGENTS.md`, `README.md`, and `RELEASE_MANIFEST.md` aligned on the v2.8.6 current baseline.
- Validation-result freshness re-check found `README.md` and `RELEASE_MANIFEST.md` aligned on the current `make test` result: `44 passed`.

## Evidence Artifacts

- This report is the G0 Evidence Lite artifact for active-docs baseline review.
- Command evidence captured in this report:
  - `make compile`: pass
  - `make test`: pass, `44 passed in 1.75s`
  - `make validate-examples`: pass, `Run validation passed`

## Antigravity Implementation Report

- Link or path: `docs/templates/antigravity_implementation_report.md` copy for this gate.

## Codex Findings

- The active/archive boundary is mostly correct and clear.
- `docs/11_ENGINEERING_CONTRACT_V2_8_3.md` and `docs/13_CONTRACT_HARDENING_V2_8_4.md` are correctly marked as historical references.
- `docs/00_PRODUCT_SPEC_V2_8.md` correctly frames itself as the v2.8 product target baseline, with v2.8.6 execution governed by active implementation docs.
- `AGENTS.md` version posture has been corrected from v2.8.5 to v2.8.6.
- `README.md` and `RELEASE_MANIFEST.md` stale validation records have been corrected to the current `make test` result: `44 passed`.
- G0 contract baseline now passes.

## Blocking Issues

- None.

## Non-blocking Issues

- None.

## Rollback Note

- No runtime, schema, controller, worker, or deployment changes were made in this G0 fix. Rollback is limited to the documentation changes in `AGENTS.md`, `README.md`, `RELEASE_MANIFEST.md`, and this report.

## Decision

- Passed. G0 contract baseline is accepted.

## Next Gate Unlock Status

- Unlocked. G1 Controller Minimum State Machine can begin under Antigravity ownership.
