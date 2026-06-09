# Runtime Artifact Hygiene Baseline

Status: pending

Purpose:
Remove inherited tracked runtime artifacts under .agentcomos/runs from the main baseline so feature branches no longer carry runtime deletion diffs.

Required checks:
- git ls-files .agentcomos/runs returns empty.
- .gitignore ignores .agentcomos/runs/.
- make compile passes.
- make test passes.
- make validate-examples passes.
- No .env, uv.lock, secrets, or runtime artifacts are committed.
- Feature branches such as R2 should no longer need to carry .agentcomos/runs deletion diffs.

Do not mark this passed. Codex will review.
