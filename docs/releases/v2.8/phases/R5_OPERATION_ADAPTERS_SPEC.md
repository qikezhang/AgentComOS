# R5 Operation Adapters Spec

## Goal

Implement controlled adapters for shell, ssh, sudo, docker, and systemctl.

## Scope

- shell adapter
- ssh adapter
- sudo adapter
- docker adapter
- systemctl adapter
- adapter result artifacts
- policy allowlists
- adapter audits
- Evidence / Delivery / GM Report integration

## Out of scope

- arbitrary commands
- unrestricted root shell
- unrestricted ssh session
- unrestricted docker exec shell

## Required tests

- allowlisted shell healthcheck works
- blocked rm -rf does not execute
- allowlisted ssh status works or safe unavailable result
- blocked arbitrary ssh does not execute
- allowlisted docker logs works
- blocked docker prune does not execute
- allowlisted systemctl status works
- blocked systemctl disable does not execute

## Acceptance criteria

- adapters only accept executor-normalized commands
- no adapter bypasses policy
- all results audited
- all outputs redacted
