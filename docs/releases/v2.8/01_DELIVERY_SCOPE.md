# 01 Delivery Scope

## Current G11 scope

Implemented by G11:

- fake/mock Discord controlled bridge
- inbound message artifact
- GM command artifact
- explicit confirmation
- Manual OS / Decision / Feynman / Loop integration
- Evidence / Delivery / GM Report integration
- no real Discord
- no shell execution
- no daemon

## v2.8 final delivery scope

The v2.8 final enterprise delivery scope includes:

- Docker Compose production service
- supervised always-on container
- real Discord Bot adapter
- Controlled Executor Framework
- controlled shell adapter
- controlled ssh adapter
- controlled sudo adapter
- controlled docker adapter
- controlled systemctl adapter
- enterprise smoke testing
- CI/release gates
- incident response
- artifact retention / backup / restore guidance
- release candidate and final release review

## Still not delivered in v2.8

v2.8 does not include:

- arbitrary command execution
- uncontrolled root access
- no-audit production execution
- Worker Evolution
- Auto Versioner
- Industrial Auto Governance
- unrestricted shell access
- unrestricted ssh access
