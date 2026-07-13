# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project

`lab-orchestration` is at the planning stage
(`Development Status :: 1 - Planning`): the tooling and packaging are complete,
but the only source code so far is a placeholder `Example` class in
`src/lab_orchestration/example.py`. That placeholder is scaffold, replace it, do
not build around it. See **Scope** for what the project is.

## Scope (locked, the four components)

1. **Orchestration engine: the spine, written from scratch.** Owns the temporal
   state machine: sequencing timed stages against an instrument, loop
   constructs, and an acquisition hook fired at defined points. Phrased
   workflow-agnostically. It does not know what a thermocycler is.
2. **qPCR reference workflow: defined on top of the engine.** Supplies the
   thermal program (temperature stages, ramps, the cycling block) and the
   fluorescence acquisition at the end of each extension step.
3. **Opentrons sample-prep module: bounded.** Plate/reagent layout and
   master-mix distribution (optionally one normalization step), against the real
   Opentrons Python API via `opentrons_simulate`. **Not** a full extraction
   protocol.
4. **Data-analysis tail.** Amplification curves → baseline subtraction →
   threshold / Cq calling → standard curve → quantification of unknowns. Melt
   curve optional.

Anything outside these four is out of scope.

## Commands

`uv` manages the environment; `nox` is the task runner (`noxfile.py` is a
self-contained uv script).

```bash
uv sync                                          # install package + dev/test deps into .venv
uv run pytest                                    # run the test suite
uv run pytest tests/test_example.py::test_add    # run a single test
uv run pytest -k subtract                        # run tests matching an expression

nox -s tests                                     # tests in an isolated nox env
nox -s lint                                      # all pre-commit hooks (via prek)
nox -s pylint                                    # pylint (installs the package; slower path)
nox -s build                                     # build sdist + wheel (default=False, name it explicitly)
```

Linting and formatting run through pre-commit (`prek run --all-files`, or
`nox -s lint`): ruff (check + format), mypy, codespell, shellcheck, prettier.
Pylint runs separately because it needs the package installed.

## Conventions that will bite you

- **Warnings are errors in tests.** `filterwarnings = ["error"]` in
  `pyproject.toml`. Any warning raised during a test fails it.
- **Strict typing, with one divergence worth knowing.** `[tool.mypy]` is strict
  and targets both `src` and `tests`. The pre-commit hook, however, runs mypy
  over `src|noxfile.py` only: the hook runs in an isolated environment that
  cannot see the editable src-layout package, so type-checking `tests` there
  fails on import. **The hook is the gate; `uv run mypy` is stricter than the
  gate.** All new code under `src/lab_orchestration/` must be fully typed.
- **Ruff runs a broad ruleset** (bugbear, pyupgrade, pathlib, pytest-style, and
  more). `T20` (no `print`) is ignored only in `tests/**` and `noxfile.py`.
- Python **>=3.12**. CI tests 3.12 and 3.14.
- **Autofix is a syntax-and-style opinion, never a semantic one.** When a hook
  rewrites a semantically loaded line (a `parametrize` names string, a regex, a
  format string), re-run the tests before trusting it.
- CI stays green. A red build is not a later problem.

## Repository facts

- **src layout.** The importable package is `src/lab_orchestration/`; tests
  import it as an installed package, so `uv sync` must have run.
- **The version is derived from git tags** via `hatch-vcs`, which generates
  `src/lab_orchestration/_version.py` at build time (git-ignored; only the
  `.pyi` stub is tracked). `__init__.py` re-exports it as `__version__`, and
  `tests/test_package.py` asserts it matches the installed metadata. **Never
  hand-edit a version.**
- **`py.typed`** marks the package as typed (PEP 561).
- Generated from the
  [`scientific-python/cookie`](https://github.com/scientific-python/cookie)
  template. `.copier-answers.yml` is Copier-managed, do not edit it by hand.
- The Scientific Python Development Guide
  (learn.scientific-python.org/development/) is the currency reference. When a
  pattern's currency is in doubt, check it there rather than relying on memory.
- **The template was trimmed from a library to an application:** no hosted docs,
  no PyPI release workflow, no dependabot. Do not reintroduce library-shaped
  tooling.
- `.github/workflows/ci.yml`: a format job (prek + pylint) and a test matrix
  (Python 3.12 and 3.14 on Ubuntu), gated by an `alls-green` pass job.

## Design constraints

These are load-bearing. Violating one is a design regression, not a style
disagreement.

- **The engine is workflow-agnostic; qPCR is the reference workflow defined on
  top of it.** Engine code must not import from, name, or special-case qPCR. If
  a capability can only be phrased in qPCR terms, it belongs in the workflow
  layer, not the engine.
- **YAGNI is the tiebreaker.** No abstraction without a present, concrete need.
  One workflow exists and one is enough, a second will not be added to "prove"
  generality. Generality is demonstrated by the seam, not by more
  implementations. When two designs are both defensible, take the simpler one.
- **Build order is not workflow order.** The engine is completed and
  independently shippable first; the Opentrons sample-prep module and the
  data-analysis tail are bolted on afterwards. The engine must depend on
  neither, both depend on the engine.
- **Opentrons is an optional dependency group, never a core dependency.** It
  pins `numpy<2` and pulls in a heavy robot stack. The engine and the data tail
  must install and run without it.
- **Synthetic data only.** No real or proprietary dataset enters this
  repository, ever. The synthetic generator stays a simple parametric curve
  (sigmoidal + baseline + noise; knobs: efficiency, starting quantity, Cq). It
  does not model reaction kinetics mechanistically. Document its assumptions.
- **No hardware.** Everything runs on a laptop against simulated instruments.

## Working agreement

- **Surface architecture decisions; do not resolve them silently.** When a task
  forks on a design question (a new abstraction, a module boundary, an interface
  shape) stop and state the fork with its options and tradeoffs. Do not pick one
  and carry on.
- Inside the established design, proceed without asking.
- **Do not propose scope.** Suggestions to add a feature, a second workflow, or
  an abstraction "for later" are out of bounds.
- Architecture decisions, once made, are recorded in the repository's decision
  docs and distilled into this file. **This file is the standing contract: if
  the code contradicts it, the code is wrong.**
- If a constraint here blocks you or looks wrong, say so — do not override it.
- **Commits: one logical change each.** If the subject line needs two verbs, it
  should have been two commits.
- **Do not commit or push.** Stage nothing, write no commit messages. Report
  what changed and stop; the commit is authored by hand.
