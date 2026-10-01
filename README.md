# lab-orchestration

<!-- prettier-ignore-start -->
[![CI][ci-badge]][ci-link]
[![Coverage][coverage-badge]][coverage-link]
[![Python][python-badge]][python-link]
[![License: MIT][license-badge]][license-link]

[ci-badge]: https://github.com/neveulouis/lab-orchestration/actions/workflows/ci.yml/badge.svg
[ci-link]: https://github.com/neveulouis/lab-orchestration/actions/workflows/ci.yml
[coverage-badge]: https://codecov.io/gh/neveulouis/lab-orchestration/graph/badge.svg?token=RU3ETJKZ34
[coverage-link]: https://codecov.io/gh/neveulouis/lab-orchestration
[python-badge]: https://img.shields.io/badge/python-3.12-blue
[python-link]: https://www.python.org/downloads/
[license-badge]: https://img.shields.io/badge/license-MIT-green
[license-link]: LICENSE
<!-- prettier-ignore-end -->

Orchestration software that runs instrument workflows, keeps a record of what
took place and computes analyses, using qPCR as the reference workflow.

## Description

The engine runs a protocol by following steps and repeated sequences. It drives
the instruments through them and records one event for each completed step. The
run is then saved to a JSON file and a stand-alone analysis step reads it again
to produce a Cq value for each well, subtracting a baseline from the recorded
fluorescence first. It then fits a standard curve over the standards and uses it
to quantify the unknowns flagging any whose Cq falls outside the standards'
range.

Two instruments are built in: a thermocycler written from scratch, and a liquid
handler running through an Opentrons simulation. The engine dispatches to both
by name so it never imports the vendor library. There is no actual hardware and
the qPCR signal is a synthetic noisy curve so the process can take place on a
machine with nothing connected to it.

## Installation

Needs Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

```bash
uv run -m lab_orchestration
```

Output:

```
Run completed, record produced at run.json
Well  Role      Cq     Quantity
A1    standard  15.91  1000.00
A2    standard  18.72  100.00
A3    standard  22.38  10.00
A4    unknown   17.87  224.53
```

The record is written to `run.json` in the working directory.

## Documentation

- [`docs/design.md`](docs/design.md) contains the details of the architecture:
  the engine/workflow seam, the instrument interface, what the run record holds
  and why.
- `docs/decisions/` summarizes architecture decisions in records with one per
  major choice.
- [`CLAUDE.md`](CLAUDE.md) defines the contract this repository hands to the AI
  coding agent, and also describes how the project was built.

## Scope

Deferred decisions:

- **No plate handoff.** The liquid handler fills a plate and the thermocycler
  reads one. Nothing moves it between them yet.
- **No command line.** The demo accepts no arguments and writes to only one
  location.
- **No controls or replicates**. Each standard and the unknown is a single well,
  and there is no no-template control.

## License

MIT.
