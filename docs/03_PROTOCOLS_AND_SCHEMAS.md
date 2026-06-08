# Protocols and Schemas

Authoritative JSON Schemas live under `schemas/`. This document explains their intent.

## Operating Intent

A GM-created task request. It is the main bridge between GM and Controller.

Required fields:

- `intent_id`
- `created_by: gm`
- `source`
- `goal`
- `success_criteria`
- `constraints`
- `risk_level`

## Worker Invocation

Created only by OpenCode. Executed by Controller. Output receiver is OpenCode.

Required invariant:

```yaml
created_by: opencode
called_by: opencode
executed_by: controller
output_receiver: opencode
gm_direct_access: false
```

## Decision Request

Created by OpenCode after Task Classification when uncertainty exists. It records Decision Need Score and decision mode.

## Feynman Check

Created for pre-execution, batch, delivery, or release checks.

## Loop Execution Request

Created by OpenCode. Executed by Controller / Loop Engine. Must include budget and stop conditions.

## Evidence Packet Manifest

Lists all artifacts required for completion.

## User Report Packet

Structured report for GM to communicate with user.
