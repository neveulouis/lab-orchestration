# 0003 — Instruments are simulated behind an interface

## Status

Accepted — 2026-07-14.

## Context

The build runs on a laptop with no hardware, no network, and no external
services, yet must showcase orchestration of an instrument suite (thermocycler,
liquid handler). It must be fully executable with simulated instruments **with
no change to engine or workflow code**, and remain extensible to real hardware
later without rewriting the engine.

## Decision

Instruments are accessed through an **interface**. The engine orchestrates
against that interface, never against a concrete instrument. Simulated
instruments implement the interface and generate synthetic readings. The
**synthetic generator belongs to the workflow** (it defines the readings), not
to the engine. The implementation is selected via run configuration; the
simulated instrument is the only implementation that exists and is the default.

## Consequences

- The engine is hardware-agnostic. Swapping simulation for a real driver is a
  new implementation of the interface, not an engine change.
- Synthetic data stays the workflow's concern; the engine stays ignorant of qPCR
  specifics.
- The instrument is the third injected-variability source, uniform with the seed
  and the clock.
- Simulated readings are seed-driven, so reproducibility depends on the seed
  reaching the simulator (ties to the seed / run-record requirements).
- Cost: an interface must be designed and maintained while only one
  implementation exists. This is justified by the "no engine change to simulate"
  requirement, **not** by a hypothetical second implementation. Do not abstract
  the interface beyond what that requirement needs.
