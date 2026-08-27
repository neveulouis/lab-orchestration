# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project

`lab-orchestration` orchestrates laboratory instrument workflows. See **Scope**.

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

uv manages the environment. noxfile.py is a self-contained uv script (PEP 723)
that carries its own copy of nox. CI invokes it as `uvx nox -s <session>` —
pylint and mypy.

```bash
uv sync                                           # install package + dev/test deps into .venv
uv run pytest                                     # run the test suite
uv run pytest tests/test_package.py::test_version # run a single test
uv run pytest -k timestamp                        # run tests matching an expression

uv run noxfile.py -s tests                        # tests in a fresh isolated env (real install of the package)
uv run noxfile.py -s pylint                       # pylint (installs the package; slower than the pre-commit hook)
uv run noxfile.py -s build                        # build sdist + wheel (default=False, name it explicitly)
uv run noxfile.py -s mypy                         # mypy over src + tests in a fresh env (installs the package)
```

Linting and formatting run through the pre-commit hook config
(`uvx prek run --all-files`): ruff (check + format), mypy, codespell,
shellcheck, prettier. Pylint runs separately because it needs the package
installed.

## Conventions that will bite you

- **Warnings are errors in tests.** `filterwarnings = ["error"]` in
  `pyproject.toml`. Any warning raised during a test fails it.
- **Strict typing, enforced by two gates.** All code in `src/` and `tests/` must
  be fully annotated — every parameter and the return. `disallow_untyped_defs`
  and `disallow_incomplete_defs` are on, so a bare `-> None` is not enough.
  - **pre-commit hook** — runs on every commit, scoped to `src` and
    `noxfile.py`.
  - **nox session** (`uv run noxfile.py -s mypy`) — runs in CI, covers `src` and
    `tests`.

  The split is not arbitrary: pre-commit runs each hook in an isolated
  environment that does not have the package installed, so mypy there cannot
  resolve `import lab_orchestration` and cannot check `tests`. The nox session
  installs the package (`-e.`), which is why it can. Do not "fix" the hook by
  widening its `files:` — it will fail on import.

- **Ruff runs a broad ruleset** (bugbear, pyupgrade, pathlib, pytest-style, and
  more). `T20` (no `print`) is ignored only in `tests/**` and `noxfile.py`.
- Python **3.12 only**. CI tests 3.12.
- **Autofix is a syntax-and-style opinion, never a semantic one.** When a hook
  rewrites a semantically loaded line (a `parametrize` names string, a regex, a
  format string), re-run the tests before trusting it.

## Repository facts

- **src layout.** The importable package is `src/lab_orchestration/`; tests
  import it as an installed package, so `uv sync` must have run.
- **The version is derived from git tags** via `hatch-vcs`, which generates
  `src/lab_orchestration/_version.py` at build time (git-ignored; only the
  `.pyi` stub is tracked). `__init__.py` re-exports it as `__version__`, and
  `tests/test_package.py` asserts it matches the installed metadata. **Never
  hand-edit a version.**

  Because `_version.py` is regenerated at install time and lives in `src/`, any
  nox session that installs the package rewrites it for the project venv too,
  leaving that venv's metadata stale. `test_version` then fails after any commit
  or merge until `uv sync --reinstall-package lab-orchestration`. That is
  environment drift, not a code defect — never edit the test or the version to
  make it pass.

- **`py.typed`** marks the package as typed (PEP 561).
- Generated from the
  [`scientific-python/cookie`](https://github.com/scientific-python/cookie)
  template. `.copier-answers.yml` is Copier-managed, do not edit it by hand.
- **Do not write commands or config from memory.** Every command in this file
  was wrong at least once because it was inferred rather than checked. Before
  proposing a command, a tool invocation, or a config pattern, verify it against
  the repo (read the file, run `--help`, run the command) or against the
  [Scientific Python Development Guide](https://learn.scientific-python.org/development/).
  A documented command that does not run is worse than no documentation.
- **The template was trimmed from a library to an application:** no hosted docs,
  no PyPI release workflow, no dependabot. Do not reintroduce library-shaped
  tooling.
- `.github/workflows/ci.yml`: a quality job (prek, pylint, mypy) and a test
  matrix (Python 3.12 on Ubuntu, Windows and macOS), gated by an `alls-green`
  pass job.

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
- **Opentrons is a core dependency. It used to be optional.** It was optional
  because it forces `numpy` below version 2 and brings a lot of packages with
  it. That is why Python must be 3.12: numpy 1.26.4 is the last version 1
  release and it does not run on 3.13. It is core now because an optional
  dependency is not installed unless someone asks for it by name, and Opentrons
  is the part a reader is most likely to look for.
- **Synthetic data only.** No real or proprietary dataset enters this
  repository, ever. The synthetic generator stays a simple parametric curve
  (sigmoidal + baseline + noise; knobs: efficiency, starting quantity, Cq). It
  does not model reaction kinetics mechanistically. Document its assumptions.
- **No hardware.** Everything runs on a laptop against simulated instruments.
- **The engine does not know about the analysis tail.** It emits a persisted run
  record and nothing downstream; both the analyses and the report are produced
  by the data tail, which reads that record after the run terminates and
  operates on nothing else. Engine code must not import, call, or reference
  analysis, nor build a report. (ADR 0001, ADR 0004)
- **The engine executes against an injected clock; it never reads wall-clock
  time or sleeps directly.** Workflows declare real durations; the engine runs
  them against a clock from run configuration, simulated by default (runs finish
  in seconds). A direct time/sleep call in engine code is a defect. (ADR 0002)
- **Run-record timestamps are logical protocol time, not wall-clock time.** They
  are accumulated from the workflow's declared step durations and are identical
  under the simulated clock or the wall-clock; the same configuration produces
  the same timeline. The record does not report real elapsed time, and building
  a timestamp from a wall-clock read is a defect. (ADR 0005)
- **The engine orchestrates against an instrument interface, never a concrete
  instrument.** Simulated instruments implement it; the synthetic reading
  generator belongs to the workflow, not the engine. Do not abstract the
  interface past the "no engine change to simulate" requirement — one
  implementation exists. (ADR 0003)

## Working agreement

- **Surface architecture decisions; do not resolve them silently.** When a task
  forks on a design question (a new abstraction, a module boundary, an interface
  shape) stop and state the fork with its options and tradeoffs. Do not pick one
  and carry on. Present the options unranked: do not mark one as recommended,
  preferred, or obvious, and do not order them so one reads that way. The
  tradeoffs are the deliverable; the choice is not yours.
- Inside the established design, proceed without asking.
- **Do not propose scope.** Suggestions to add a feature, a second workflow, or
  an abstraction "for later" are out of bounds.
- Architecture decisions, once made, are recorded in the repository's decision
  docs and distilled into this file, each distilled constraint citing its source
  ADR. **This file is the standing contract: if the code contradicts it, the
  code is wrong.**
- If a constraint here blocks you or looks wrong, say so — do not override it.
- **Commits: one logical change each.** If the subject line needs two verbs, it
  should have been two commits.
- **Do not commit or push.** Stage nothing, write no commit messages. Report
  what changed and stop; the commit is authored by hand. A deny rule in
  `.claude/settings.json` enforces this, but that file is untracked and local to
  one machine. A fresh clone has the rule as prose only.
- **Do not report a check as run unless its output is in the reply.** Report
  each one separately; a single line covering several stands for none of them.
- **Division of work.** Louis writes the code that carries design: the
  orchestration engine's state machine and its public surface, the
  engine/workflow boundary, and all tests. Claude may write _skeletons_ for
  these — signatures, type annotations, docstrings stating the contract,
  `NotImplementedError` bodies — but not implementations. Claude may write
  plumbing that carries no design decision: CLI wiring, file I/O, the synthetic
  data generator, and refactors already decided. All of it is reviewed. When
  unsure which side a piece falls on, ask. Do not assume.

## Project state

`project-state.md` at the repository root (untracked) is the project-management
layer: phase, next step, carry-forwards, session log. It is not documentation
and it is not a decision doc.

- **Append to the session log; edit sections in place. Never regenerate the
  file.** A rewrite silently drops content that was not in the immediate
  context. This has happened before.
- Write an entry only if the session moved something.
- Report the change and stop. Do not commit it.
- **Auto-memory is off** (`"autoMemoryEnabled": false` in
  `.claude/settings.json`). Memory files are authored, not accumulated: this
  file and `project-state.md` are written deliberately and reviewed. Do not
  propose re-enabling it.
