# PR and Review Workflow — v2.8.6

> 中文备注：本文件定义 Codex 和 Antigravity 的 PR 流程，确保开发结果可审计、可测试、可回滚。

## PR Types

```text
contract-docs
schema-change
runtime-implementation
deployment-change
worker-spec-change
acceptance-gate
hotfix
```

## Required reviewers

```text
contract-docs -> Codex
schema-change -> Codex + Antigravity if runtime affected
runtime-implementation -> Antigravity + Codex acceptance
worker-spec-change -> Codex boundary review + Antigravity runtime feasibility
```

## Required checklist

Every PR must include:

```text
phase gate
changed files
tests run
examples updated
evidence artifacts
risk assessment
rollback note
```

## Merge rule

No merge unless:

```bash
make compile
make test
make validate-examples
```

Runtime PRs additionally require generated logs / events / artifacts.
