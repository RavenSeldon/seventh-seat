# agents (PRE-SPRINT, declared)

Provider adapters, schema-checked world tools, private histories, persistent budget
reservations, response cache and bounded episode runner. See
[Wednesday harness](../../../docs/WEDNESDAY_HARNESS.md) for commands, validation,
pricing assumptions and remaining qualification work. Offline tests use only the
standard library; live calls use the pinned optional `providers` dependencies.

The live CLI is restricted to a no-hazard engineering fixture. It does not run
qualification, calibration or evaluation, and does not configure E/S interventions.
