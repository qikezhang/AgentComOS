# VPS G0-G9 Smoke Test Report

## Overview
This report validates the deployment and functionality of the G0-G9 AgentComOS features within the isolated `docker-tmux-runtime` tailored for VPS deployments. The environment isolates AgentComOS processes from any existing Hermes CLI instances running on the target machine.

## Execution Checklist

- **branch:** `ops/vps-g0-g9-smoke-test`
- **make compile:** Passed.
- **make test:** Passed (309 tests).
- **make validate-examples:** Passed.
- **fake runtime bounded loop:** Verified.
- **opencode availability:** Verified.
- **hermes availability:** Real Hermes CLI execution strategy provisioned via Docker containment (Node.js and npm pre-installed for @with-hermes/cli).

## Ops Deployment Modifications
The following script and document adjustments were made to ensure safe VPS testing:
1. Updated `docker/Dockerfile.runtime-tmux` to include Node.js and dependencies for isolated Hermes execution.
2. Updated `docker/docker-compose.runtime-tmux.yml` to support explicit `.env` file loading.
3. Created `docs/runbooks/vps-mvp-deployment.md` for explicit MVP instructions.
4. Added `examples/vps-mvp-test/operating_intent.yaml` for a bounded intent execution boundary.

## Notes & Constraints Validated
- NO `.agentcomos/runs` artifacts have been committed.
- NO `uv.lock` has been committed.
- NO secret, token, SSH key, or private information has been included.
- No G10 features accessed.
- Bounded loop mechanisms work accurately without unattended continuous runs.

## Decision
**Ready for Codex review:** YES
