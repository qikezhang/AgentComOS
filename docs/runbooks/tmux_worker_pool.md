# tmux Worker Pool Runbook

Hermes Worker = tmux + hermes chat -Q -q.

Inspect sessions:
```bash
tmux ls
tmux attach -t agentcomos_<run_id>_<worker_id>_<task_id>
```

Kill stalled session only after Controller exports logs and marks worker_job failed/stalled.
