# 0008 — Opentrons is a core dependency

## Status

Accepted — 2026-09-01.

## Context

During pre-project, it was decided the opentrons module would be an optional
dependency group because the library pins `numpy` below version 2 and it was
thought that it would bring heavy machinery with it. Adding it as extra would
keep it off the engine and the data tail so the spine-only install would stay
light and use current numpy.

Only 30 packages were installs with the library, which is not heavy. The numpy
pin is real on the other hand (1.26.4, last version 1).

## Decision

It was decided that `opentrons` is a core dependency. `requires-python` is
`>=3.12,<3.13` for the whole project.

An optional dependency is not installed unless someone asks for it by name, and
the Opentrons module is the part a reader is most likely to look for.

## Consequences

- The extra would have kept the published Python range at `>=3.10` and let a
  spine-only install skip the pin. That range is gone. Anyone on 3.13 cannot
  install this project at all, including the parts that never touch a robot.
- The python ceiling comes from a dependency of a dependency. `pyproject.toml`
  does not say why the upper bound is there, so `CLAUDE.md` does. Re-read the
  pin at every `opentrons` upgrade.
- The engine and the data tail no longer run without `opentrons` installed, but
  they must still run without importing it. Only the sample-prep module and its
  wiring may.
- Installing is not importing. Every wheel here is `py3-none-any`, so it
  installs anywhere and that proves nothing about loading.
  `tests/test_opentrons_smoke.py` is what proves it, on Ubuntu, Windows and
  macOS.
