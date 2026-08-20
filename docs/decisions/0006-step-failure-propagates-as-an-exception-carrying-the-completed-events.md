# 0006 — Step failure propagates as an exception carrying the completed events

## Status

Accepted — 2026-08-20.

## Context

A step fails when the instrument refuses the operation: a named operation not
recognised, or a request its state does not allow. The run terminates (fail-
fast), but the steps that already completed are worth keeping.

Two things must leave the program: the failure, and the events accumulated
before it. Two ways to carry them: return them or raise them.

Return is the obvious choice but the walk recurses. `run_program` calls itself
on every repeat block, so a failure inside a block needs to cross every nesting
level on its way out.

## Decision

Failure propagates as a raised exception carrying the completed events. One
function above the walk catches it and names the terminal state.

## Consequences

- Returning requires every nesting level to inspect its block's result and re-
  propagate by hand. The raise crosses them all on its own.
- Shifting the partial trace's timestamps into run time stays in one place.
- A caller cannot discard a failure by ignoring a return value.
- Cost: the walk returns a list of events and raises an exception holding a list
  of events.
- Both instrument failure types collapse into one terminal state. The
  distinction survives only as text in the recorded reason.
