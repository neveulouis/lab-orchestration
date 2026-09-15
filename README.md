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
in order to produce a Cq value from the recorded fluorescence.

Two instruments are built-in: a thermocycler written from scratch, and a liquid
handler running through an Opentrons simulation. The engine dispatches to both
by name so it never imports the vendor library. There is no actual hardware and
the qPCR signal is a synthetic curve so the process can take place on a machine
with nothing connected to it.

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
Well  Cq
A1    15.56
A2    15.56
A3    15.56
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

- **No plate layout.** Three wells, all replicates of one sample. Nothing marks
  a well as a standard or with a known quantity, so the standard curve and
  quantification stay out for now.
- **No plate handoff.** The liquid handler fills a plate and the thermocycler
  reads one. Nothing moves it between them yet.
- **A noiseless curve.** The curve is just a simple logistic equation with no
  offset and no noise. Since nothing is there to subtract, there is no baseline
  subtraction. Replicates read identically, which is why the three wells above
  show the same Cq.
- **No command line.** The demo accepts no arguments and writes to only one
  location.

## License

MIT.
