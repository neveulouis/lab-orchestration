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
the instrument through them and records one event for each completed step. The
run is then saved to a JSON file and a stand-alone analysis step reads it again
in order to produce a Cq value from the recorded fluorescence.

The instruments are simulated. There is no actual hardware and the qPCR signal
is a synthetic curve so the process can take place on a machine with nothing
connected to it.

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
Cq: 15.56
```

The record is written to `run.json` in the working directory.

## Documentation

- `docs/design.md` contains the details of the architecture: the engine/workflow
  seam, the instrument interface, what the run record holds and why.
- `docs/decisions/` summarizes architecture decisions in records with one per
  major choice.
- `CLAUDE.md` defines the contract this repository hands to the AI coding agent,
  and also describes how the project was built.

## Scope

Deferred decisions:

- **One well only.** A single well is a true reduction of a thermocycler, since
  the block heats every well at once. It stops being one when a liquid handler
  enters, which is when wells arrive and with them the standard curve and
  quantification, which both need multiple wells with known quantities.
- **A noiseless curve.** The curve is just a simple logistic equation with no
  offset and no noise. Since nothing is there to subtract, there is no baseline
  subtraction.
- **No command line.** The demo accepts no arguments and writes to only one
  location.
- **One instrument per run.** A step names an operation, not an instrument.
  Adding a second instrument would need a mapping from operations to
  instruments.

## License

MIT.
