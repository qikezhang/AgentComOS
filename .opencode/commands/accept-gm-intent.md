# accept-gm-intent

Read the Operating Intent and Runtime Context Bundle.

Required steps:

1. Perform Task Classification.
2. Calculate Decision Need Score.
3. If uncertainty exists, create Decision Market Request.
4. Create Feynman pre-execution check for non-trivial tasks.
5. Create Project Plan, Task Frontier Seed, Loop Execution Request, or Worker Invocation as appropriate.
6. Do not call Worker directly except by writing Worker Invocation for Controller.
7. Write required outputs to the run directory.
