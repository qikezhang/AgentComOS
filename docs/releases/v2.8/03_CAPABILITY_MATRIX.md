# 03 Capability Matrix

| Capability | Current G11 Status | v2.8 Final Target | Production Default | Notes / Gates |
|---|---:|---:|---:|---|
| Controller state machine | done | yes | yes | G1 passed |
| Fake OpenCode runtime | done | yes | yes | G2 passed |
| Real OpenCode availability | availability probe | yes | partial | G3 passed as availability probe |
| Fake Hermes Worker | done | yes | yes | G4 passed |
| Real Hermes availability | availability probe | yes | partial | G5 passed as availability probe |
| Evidence / Delivery / GM Report | done | yes | yes | G6 passed |
| Program / Frontier | done | yes | yes | G7 passed |
| Decision / Feynman | done | yes | yes | G8 passed |
| Bounded Loop | done | yes | yes | G9 passed |
| Manual OS | done | yes | yes | G10 passed |
| GM Discord fake bridge | done | yes | no | G11 |
| Docker Compose deployment | partial / ops smoke only | yes | yes | R2 |
| Docker supervised service | no | yes | yes | R2 |
| Real Discord Bot | no, fake adapter only | yes | yes | R3 |
| Discord read-only commands | fake only | yes | yes | R3 |
| Discord controlled write commands | fake only | yes | yes, behind policy | R3 + R4 |
| Controlled Executor | no | yes | yes | R4 |
| Shell execution | no | yes | yes, controlled only | R4 + R5 |
| SSH execution | no | yes | yes, controlled only | R4 + R5 |
| Sudo execution | no | yes | yes, controlled only | R4 + R5 |
| Docker execution | no | yes | yes, controlled only | R4 + R5 |
| Systemctl execution | no | yes | yes, controlled only | R4 + R5 |
| Permission conflict resolution | no | yes | yes | R3 + R4 |
| Token incident response | no | yes | yes | R3 + R6 |
| CI release gates | partial | yes | yes | R6 |
| Artifact retention / backup / restore | partial | yes | yes | R6 |
| Arbitrary command execution | no | no | no | never allowed |
| Worker Evolution | no | no | no | future post-v2.8 |
| Auto Versioner | no | no | no | future post-v2.8 |
| Industrial Auto Governance | no | no | no | future post-v2.8 |
