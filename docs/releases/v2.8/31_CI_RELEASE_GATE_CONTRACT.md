# 31 CI Release Gate Contract

## Goal

v2.8 release branches must be protected by repeatable release gates.

## Required CI gates

- make compile
- make test
- make validate-examples
- secret scan
- no `.agentcomos/runs` in diff
- no `.env` in diff
- no private key in diff
- no real Discord token in diff
- docs/releases/v2.8 manifest exists
- Docker compose config validates
- schema examples validate
- blocked command tests pass

## Suggested GitHub Actions jobs

- `compile`
- `test`
- `validate_examples`
- `secret_scan`
- `artifact_pollution_scan`
- `docker_compose_config`
- `docs_manifest_check`

## Failure behavior

Any failed gate blocks release candidate creation.
