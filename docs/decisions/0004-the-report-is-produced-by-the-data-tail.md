# 0004 — The report is produced by the data tail, not the engine

## Status

Accepted — 2026-07-17.

## Context

A run produces two things at the end: a persisted run record and a human-facing
report. ADR 0001 established that analysis is a post-hoc consumer of the run
record and that the engine does not know the data tail, but it left open where
the report is produced. The requirements initially placed report generation in
the engine ("create a report when a run is finished").

Two placements were live:

1. The engine produces the report when the run finishes.
2. The report is produced after the run by the data tail, from the run record
   and the analyses built on it.

A useful report presents analysis results, not a bare run summary. Under option
1 the engine would therefore need analysis results to build the report, which
pulls analysis back into the run and forces the engine to depend on the data
tail — contradicting ADR 0001.

## Decision

The report is produced by the data tail, after the run terminates, from the run
record and the analyses built on it. The engine's sole end-of-run output is the
run record, which already carries the terminal state and its reason. The engine
does not author the report.

## Consequences

- Nothing human-facing depends on the engine. The engine's entire output is the
  run record; the report and analyses are built downstream of it by the layer
  that is allowed to be workflow-aware. This is the strongest form of the
  engine/analysis separation stated in ADR 0001.
- The report may combine the run summary and analysis results, since it is
  produced by the data tail.
- The requirement previously filed under the engine ("create a report when a run
  is finished") moves to the data & analyses section: the report is produced
  from the record after analysis, not by the engine at run end.
  (`docs/requirements.md` updated accordingly.)
- Cost: there is no engine-only report. A minimal "run completed" signal, if
  needed, is the terminal state carried in the run record, not a report.
