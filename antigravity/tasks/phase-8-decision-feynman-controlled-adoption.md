# Phase 8: Decision and Feynman Controlled Adoption

## Goals
1. Implement Decision and Feynman explicit trigger mechanism.
2. Allow Task Frontier to declare `decision_required` or `feynman_required`.
3. Block tasks when decision/feynman is required but missing.
4. Unblock tasks when decision/feynman result is completed.
5. Generate auditable artifacts, events, timeline.
6. Do NOT automatically trigger decision/feynman or enter loop execution.
