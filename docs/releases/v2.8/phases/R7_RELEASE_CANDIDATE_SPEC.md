# R7 Release Candidate Spec

## Goal

Create v2.8.0-rc1 after R6 passes.

## Required conditions

- R1-R6 acceptance reports passed.
- main is clean.
- CI gates passed.
- production smoke passed.
- release notes completed.
- known limitations accurate.
- go/no-go checklist completed.

## Required actions

- update release notes
- create tag `v2.8.0-rc1`
- run from-zero deployment smoke
- archive smoke reports

## Out of scope

- new features
- broad refactors
