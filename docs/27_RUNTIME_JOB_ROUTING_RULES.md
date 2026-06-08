# Runtime Job Routing Rules

> 中文备注：本文件定义 runtime job 的路由字段、执行结果字段和状态字段边界。Controller / CLI 在 `collect`、`status`、`recover` 时必须遵守本规则，避免把真实 runtime 不可用的 job 错误路由到 fake handler。

## 1. Field Classes

### Routing Fields

Routing fields decide which runtime handler owns a job:

```text
runtime
attempted_real_opencode
future: attempted_real_hermes
future: worker_runtime
```

Examples:

```yaml
runtime: fake_opencode
```

```yaml
runtime: real_opencode
attempted_real_opencode: true
```

### Execution Result Fields

Execution result fields only describe whether a real or fake tool path actually executed successfully:

```text
real_opencode_used
real_hermes_used
fake_runtime
```

These fields do not by themselves define the job type. In particular, `real_opencode_used: false` means real OpenCode did not successfully execute; it does not mean the job is fake.

### Status Fields

Status fields only describe the current job result:

```text
status
failure_reason
blocked_reason
unavailable_reason
```

These fields must not be used as fake/real routing substitutes. For example, `status: unavailable` can be a real runtime job when the real runtime was attempted but unavailable.

## 2. OpenCode Routing Contract

For OpenCode jobs, `collect`, `status`, and `recover` must route to the same runtime family that owns the job.

If the job YAML says:

```yaml
runtime: fake_opencode
```

then `collect`, `status`, and `recover` must use the fake OpenCode handler.

If the job YAML says:

```yaml
runtime: real_opencode
```

then `collect`, `status`, and `recover` must use the real OpenCode handler.

If the job YAML says:

```yaml
attempted_real_opencode: true
```

then `collect`, `status`, and `recover` must use the real OpenCode handler even when:

```yaml
real_opencode_used: false
```

Reason: `real_opencode_used: false` only says real OpenCode did not successfully execute. It does not say the job is a fake OpenCode job.

## 3. Forbidden Routing

Implementations must not use `real_opencode_used` alone to decide fake versus real job type.

Forbidden:

```python
if real_opencode_used == True:
    route_real()
else:
    route_fake()
```

Required:

```python
if runtime == "real_opencode" or attempted_real_opencode == True:
    route_real()
elif runtime == "fake_opencode" or fake_runtime == True:
    route_fake()
else:
    fail_safely()
```

`runtime` has priority over execution result fields. Unknown or missing runtime identity must fail safely and must not default to fake.

## 4. Real Unavailable Job Example

A real OpenCode job can be unavailable and still belong to the real handler:

```yaml
runtime: real_opencode
attempted_real_opencode: true
real_opencode_used: false
fake_runtime: false
status: unavailable
unavailable_reason: opencode not found
```

This job must route to the real OpenCode `status`, `collect`, and `recover` handler. It must not fall back to fake collect because the fake delivery artifacts are expected to be absent.

## 5. Fake Job Example

A fake OpenCode job remains owned by the fake handler:

```yaml
runtime: fake_opencode
fake_runtime: true
real_opencode_used: false
status: completed
```

This job must route to the fake OpenCode `status`, `collect`, and `recover` handler.

## 6. Future Hermes / tmux Worker Rule

The same classification applies to Hermes / tmux worker runtime jobs.

Example:

```yaml
runtime: hermes_tmux
attempted_real_hermes: true
real_hermes_used: false
status: unavailable
unavailable_reason: hermes not found
```

This job must still route to the Hermes / tmux worker handler. It must not fall back to a fake worker handler just because `real_hermes_used: false`.

## 7. Acceptance Requirement

Every runtime gate that introduces or modifies a real/fake runtime pair must include tests proving:

```text
unavailable real jobs still route to real status handler
unavailable real jobs still route to real collect handler
runtime field has priority over execution result fields
unknown runtime fails safely and does not default to fake
fake jobs still route to fake handler
```
