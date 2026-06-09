# 33 Permission Resolution Rules

## Core rules

1. deny overrides allow
2. unknown defaults to block
3. missing policy defaults to block
4. high-risk requires explicit policy
5. arbitrary command always blocked
6. disabled bot blocks inbound processing
7. disabled executor blocks execution
8. command allowlist is required even for admin users

## Evaluation order

```text
bot enabled?
→ token available?
→ guild allowed?
→ channel allowed?
→ user allowed?
→ role allowed?
→ command parsed?
→ command risk classified?
→ policy exists?
→ command_ref allowlisted?
→ executor enabled?
→ adapter policy allowed?
```

First failing check blocks the command.

## Required artifact

Every decision must write `permission_result.yaml` containing:

- subject user hash
- channel id
- roles hash or role names if non-sensitive
- command risk
- allow/deny decision
- reason
- evaluated_at
