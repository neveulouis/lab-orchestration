# 0005 — The run record stores logical protocol time, not wall-clock time

## Status

Accepted — 2026-07-17.

## Context

Workflow steps declare real durations, and the engine executes against an
injected clock (ADR 0002), simulated by default so a run completes in seconds.
When the engine timestamps events and readings in the run record, two sources of
time are available:

1. Logical protocol time — the timeline the workflow declares, accumulated from
   its steps' declared durations.
2. Real elapsed (wall-clock) time — how long the run actually took to execute.

ADR 0002 noted that a wall-clock changes timestamps, not scientific data, but it
did not pin what the record's timestamps mean. A naive implementation would
reach for real timestamps (`now()`), which would make the recorded timeline
depend on how fast the machine happened to run and would differ between two runs
of the same configuration.

## Decision

The run record stores logical protocol time. Timestamps are built by
accumulating the workflow's declared durations, and are independent of clock
mode: the same configuration produces the same timeline whether run under the
simulated clock or the wall-clock.

## Consequences

- Timestamps in the record are reproducible and are a property of the protocol,
  not of the machine or the particular run. Two runs of the same configuration
  produce identical timelines.
- Clock mode affects only how long the operator waits, never the values
  recorded. Wall-clock mode remains available as a pacing convenience.
- Cost: the record does not report how long a run took in real time. This is
  deliberate — real elapsed time is treated as an artifact of the run
  environment, not as data.
- A direct wall-clock read in engine code remains a defect (ADR 0002); this
  decision is about what the recorded timeline means, not about reintroducing
  wall-clock reads.
