# Module 07: Decision and Feynman Controlled Adoption

## Overview
Phase G8 introduces the Decision and Feynman engines in a "Controlled Adoption" mode.
This means that Decision and Feynman artifacts are explicitly requested by humans or external tools via CLI commands.
The system does not automatically trigger the creation of a Decision Market or perform Feynman checks autonomously.

## Explicit Mode
All Decision and Feynman requests MUST be invoked with `--mode explicit`.
If the explicit mode flag is missing or invalid, the command must fail.
Controller tick will NOT automatically generate Decision or Feynman artifacts, nor will it invoke real runtime execution.

## Task Frontier Integration
The Task Frontier introduces two new task dependencies:
- `decision_required: true`
- `feynman_required: true`

When a task requires a decision and the `decision_result` does not exist, the task state is `awaiting_decision` and blocked from execution.
When a task requires a feynman check and the `feynman_result` does not exist, the task state is `awaiting_feynman` and blocked from execution.
Once explicitly generated, a completed decision result or a passed feynman result will unblock the task.
A failed feynman result will permanently block the task unless overridden (override not implemented in G8).

## Limitations
- No automatic Decision Market or multi-agent debate.
- No automatic Feynman checks.
- No Loop Execution or Worker Evolution.
- Real Hermes and OpenCode are NOT called.
