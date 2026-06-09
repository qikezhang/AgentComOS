# 27 Executor Non-B

ypass Rules

This document defines mandatory non-bypass rules for v2.8 final delivery.

## Rule 1: Discord never directly executes

Discord adapter may only create inbound artifacts, permission results, and GM commands.

Forbidden:

- Discord adapter directly calling shell
- Discord adapter directly calling ssh
- Discord adapter directly calling sudo
- Discord adapter directly calling docker
- Discord adapter directly calling systemctl

## Rule 2: Executor never executes raw arbitrary commands

Controlled Executor must resolve a `command_ref` from policy. Raw free-form commands are blocked unless they exactly match an allowlisted command template after schema validation.

## Rule 3: Adapters never accept free-form shell text

Operation adapters receive normalized executor commands only.

## Rule 4: Every execution must produce artifacts

Required artifacts:

- permission_result.yaml
- executor_command.yaml
- executor_policy.yaml or policy reference
- executor_result.yaml
- executor_audit.md
- events
- timeline entry

## Rule 5: Failed / blocked cannot be reported as completed

Delivery Packet and GM Report must preserve blocked, failed, partial, and requires_approval states.

## Rule 6: Secrets never appear in artifacts

Outputs must pass redaction before being written.
