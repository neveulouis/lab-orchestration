# 0007 — A run drives several instruments and each step names its own

## Status

Accepted — 2026-08-27.

## Context

Until now a run drove only one instrument. This was embedded in the code but not
a rule. `design.md` states that a step names nothing beyond its operation where
one instrument is enough to make that unambiguous. The condition stops holding
when a second instrument enters: the liquid handler.

Two different ways to run the instruments. Either two runs, one per instrument
where the sample prep would finish before the thermocycler starts. Or one run
with a program that carries both instruments and requires each step to say which
instrument it belongs to.

Two separate runs is closer to what the bench does with a person carrying the
plate between the machines and would not require an engine change.

## Decision

It was decided to have one run driving both instruments. A step names its
instrument alongside the operation. The engine holds a name-to-instrument
mapping and dispatches each step to the one its step names. An event records the
instrument that produced it.

Sequencing work across instruments is what an orchestration engine is for.
Driving one instrument per run executes instrument programs, which is a smaller
claim than this project makes about itself.

## Consequences

- Two runs would have left the engine untouched and modelled the handoff the
  bench actually performs. This record describes as continuous something a
  person interrupts, and nothing in it marks the gap.
- The instrument interface does not change. What changes is who the engine hands
  the operation to.
- A serialised event gains a fourth key. Additive for a reader of the format,
  but `read_record` passes the file's keys to `Event` as keyword arguments, so
  writer and reader change together.
- A failed step still emits no event, so a failed run names neither the
  operation nor the instrument that failed (ADR 0006).
- Engine-side validation gains a second thing to check: that every instrument a
  step names was supplied. Not built here.
