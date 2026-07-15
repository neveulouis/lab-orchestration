# 0001 — Analysis is a post-hoc consumer of the run record

## Status

Accepted — 2026-07-14.

## Context

The system must both orchestrate a run and analyse its output (for qPCR: cycle
thresholds, quantification, standard curves). Two placements were live:

1. Analysis as an orchestrated step _inside_ the run, driven by the engine.
2. Analysis as a _separate consumer_ that reads the persisted run record after
   the run reaches a terminal state.

Option 1 forces the engine to know about the data tail (what analyses exist,
what they need) which couples the orchestration spine to qPCR-specific
downstream concerns and breaks the engine/workflow separation the build is built
around.

## Decision

The analysis tail is a separate consumer. It runs after the run terminates and
operates **solely** on the persisted run record. The engine emits the run record
and knows nothing about downstream analysis.

## Consequences

- The run record becomes the single contract between engine and analysis. The
  engine stays workflow- and analysis-agnostic.
- Analysis is independently testable against a fixed run record, with no engine
  run required.
- Ship-the-spine-alone stays valid: engine + run record is a complete,
  defensible outcome without the tail.
- Cost: the run record must carry everything analysis needs. Any analysis input
  not in the record is unavailable, which forces the record's schema to be
  designed deliberately (see the run-record design).
- Cost: a new analysis need may require a run-record schema change (a wider
  blast radius than a change local to the analysis code).
