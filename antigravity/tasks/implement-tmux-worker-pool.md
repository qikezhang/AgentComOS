# Antigravity Task: tmux Hermes Worker Pool

Implement a wrapper around tmux + Hermes CLI only.

Do not implement a custom Worker daemon.

Required command shape:

```bash
tmux new-session -d -s <session> "cd <worktree> && hermes chat -Q -q 'Read <invocation> and write outputs to <output_dir>/'"
```
