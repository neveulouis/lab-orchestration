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
Well  Role      Cq     Quantity
A1    standard  12.30  10000.00
A2    standard  12.14  10000.00
A3    standard  12.34  10000.00
A4    unknown   14.44  2220.93
A5    unknown   13.94  3128.26
A6    unknown   14.27  2495.63
A7    unknown   14.17  2677.26
B1    standard  15.57  1000.00
B2    standard  16.01  1000.00
B3    standard  15.46  1000.00
B4    unknown   16.72  455.45
B5    unknown   17.02  370.78
B6    unknown   16.69  467.01
B7    unknown   17.19  330.43
C1    standard  18.73  100.00
C2    standard  18.77  100.00
C3    standard  18.88  100.00
C4    unknown   21.94  12.21
C5    unknown   22.32  9.42
C6    unknown   22.02  11.54
C7    unknown   22.14  10.63
D1    standard  22.40  10.00
D2    standard  22.20  10.00
D3    standard  22.26  10.00
D4    unknown   27.43  0.27
D5    unknown   27.32  0.29
D6    unknown   27.50  0.26
D7    unknown   27.17  0.32
E1    standard  25.66  1.00
E2    standard  25.51  1.00
E3    standard  25.46  1.00
F1    standard  28.64  0.10
F2    standard  28.73  0.10
F3    standard  29.01  0.10
G1    standard  32.26  0.01
G2    standard  32.21  0.01
G3    standard  32.32  0.01
H1    NTC       —      —
H2    NTC       —      —
H3    NTC       —      —
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
- **No per-sample analysis.** Replicates are reported well by well, with no mean
  Cq or spread per sample, and nothing checks that the NTCs stayed negative.

## License

MIT.
