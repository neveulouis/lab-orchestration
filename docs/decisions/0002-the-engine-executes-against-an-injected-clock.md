# 0002 — The engine executes against an injected clock

## Status

Accepted — 2026-07-14.

## Context

qPCR steps have real durations (minutes to hours), and workflows need to express
them. Duration is part of the protocol and belongs in the run record and report.
But executing against wall-clock time would make a full run, and therefore the
test suite, take hours, and would make timing non-deterministic.

The tension: durations must be _declarable_ by the workflow without the engine
being forced to _wait_ them out.

## Decision

Workflows declare real durations in the workflow definition. The engine never
sleeps on wall-clock directly; it executes against a **clock injected via the
run configuration**. A **simulated clock is the default**: it advances declared
durations logically and completes the run in seconds without waiting. A
wall-clock is available for when real timing is wanted.

## Consequences

- Runs and tests complete in seconds by default; the multi-hour test suite is
  avoided.
- Durations stay a property of the workflow, not hard-coded engine behaviour.
- The clock is one of three injected-variability sources (with the seed and the
  instrument): each is supplied through run configuration and defaults to
  simulation, a single shape the engine treats uniformly.
- Cost: the engine must take the clock as an injected dependency rather than
  calling `time`/`sleep`. Any direct wall-clock call in engine code is a defect.
- Note: wall-clock changes timestamps, not scientific data. The data is
  seed-driven, not time-driven, so a wall-clock run is not expected to change
  results.
