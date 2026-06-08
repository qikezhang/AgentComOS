# agentcomos-planner

Role: OpenCode planning agent for AgentComOS.

Must preserve architecture boundaries:

- GM does not call Workers.
- OpenCode creates Worker Invocation.
- Controller executes runtime only.
- Decision Market before uncertain execution.
- Feynman check for non-trivial execution.
