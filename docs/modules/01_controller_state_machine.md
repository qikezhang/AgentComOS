# Controller State Machine

Controller is deterministic. It owns run/job/worker/loop/release state, not business judgment.

## Run states
submitted -> accepted -> planning -> decision -> feynman_precheck -> executing -> evidence_verifying -> release_review -> versioning -> delivered

Failure branches: blocked, paused, failed.

## Requirements
- Every transition writes run_status.yaml.
- Controller restart must rebuild active jobs from state files.
- Controller may retry mechanical failures; it may not choose a Worker or approve content quality.
