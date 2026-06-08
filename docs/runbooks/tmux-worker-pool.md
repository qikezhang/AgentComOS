# tmux Worker Pool Runbook

## Scope

This runbook covers G4 only: tmux launches the deterministic fake Hermes worker. Real Hermes execution remains G5.

## Start fake worker

```bash
agentcomos worker start --invocation examples/techai8/run/OI-TECHAI8-001/worker_invocations/HWI-TF-001.yaml --fake
```

The tmux session name is stable:

```text
agentcomos-<run_id>-<task_id>
```

Example:

```text
agentcomos-OI-TECHAI8-001-TF-001
```

## Collect outputs

```bash
agentcomos worker collect --job HWJ-OI-TECHAI8-001-TF-001-001
```

Collection requires every listed `required_outputs` file, including `DONE.md`. Missing outputs mark the job stalled or failed and must not be treated as completed.

## tmux unavailable

If `tmux` is not on `PATH`, `worker start --fake` records an unavailable worker job and reports the reason. It must not mark the job completed.

CI may use fake-no-tmux tests or monkeypatch tmux calls. Host-systemd and local Mac profiles may run the real tmux fake-worker E2E.

## Inspect and recover

```bash
agentcomos worker status --job HWJ-OI-TECHAI8-001-TF-001-001
agentcomos worker list --run OI-TECHAI8-001
agentcomos worker recover --run OI-TECHAI8-001
```

Recover reads existing worker jobs and output artifacts. It appends a recovery event and does not delete worker outputs.

## Kill

```bash
agentcomos worker kill --job HWJ-OI-TECHAI8-001-TF-001-001
```

Kill only targets the recorded tmux session. It does not delete worker outputs.

## Boundary

G4 tmux commands may only run `scripts/fake_hermes_worker.py`. Real Hermes commands are reserved for G5.

