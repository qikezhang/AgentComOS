# Loop Execution

Loop Execution executes batches selected by Task Frontier. It does not perform strategy.

## Queue types
- Manual Queue: explicit small tasks
- Dynamic Queue: bounded expansion from Task Frontier

## Hard rules
- max_parallel_workers <= 3
- max_tasks_per_batch <= 9
- budget and stop conditions required
- batch cannot continue after blocking Feynman veto
