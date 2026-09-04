# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Scope (locked, the four components)

1. **Orchestration engine: the spine, written from scratch.** Owns the temporal
   state machine: timed stages, loop constructs, acquisition hook. Phrased
   workflow-agnostically, it does not know what a thermocycler is.
2. **qPCR reference workflow: defined on top of the engine.** Supplies thermal
   program and fluorescence acquisition at each extension step.
3. **Opentrons sample-prep module: bounded.** Plate/reagent layout and
   master-mix distribution, against the real Opentrons Python API via
   `opentrons_simulate`. **Not** a full extraction protocol.
4. **Data-analysis tail.** Curves → baseline subtraction → threshold/Cq →
   standard curve → quantification. Melt curve optional.

Anything outside these four is out of scope.

## Commands

uv manages the environment. `noxfile.py` is a self-contained uv script (PEP 723)
carrying its own copy of nox. CI invokes it as `uvx nox -s <session>`, pylint
and mypy.

```bash
uv sync                                           # install package + dev/test deps into .venv
uv run pytest                                     # run the test suite
uv run pytest tests/test_package.py::test_version # run a single test
uv run pytest -k timestamp                        # run tests matching an expression

uv run noxfile.py -s tests                        # tests in a fresh isolated env (real install)
uv run noxfile.py -s pylint                       # pylint (installs the package. Slower than the pre-commit hook)
uv run noxfile.py -s mypy                         # mypy over src + tests in a fresh env (installs the package)
uv run noxfile.py -s build                        # build sdist + wheel (default=False, name it)
```

Linting and formatting run through the pre-commit hook config
(`uvx prek run --all-files`): ruff (check + format), mypy, codespell,
shellcheck, prettier. Pylint runs separately because it needs the package
installed.

## Conventions that will bite you

- **Warnings are errors in tests, except `ResourceWarning`.**
  `filterwarnings = ["error", "default::ResourceWarning"]` in `pyproject.toml`,
  filters apply last to first. The exemption exists because
  `opentrons_shared_data` opens thirteen JSON files it does not close, and under
  `["error"]` those surfaced during test setup and the test never ran. It is
  `default` rather than `ignore` so the thirteen stay visible in the output. Do
  not remove it without re-running the suite.
- **Strict typing.** All code in `src/` and `tests/` is fully annotated. Every
  parameter and the return. A bare `-> None` is not enough. Two gates: the
  pre-commit hook (scoped to `src` and `noxfile.py`) and the nox session
  (`-s mypy`, runs in CI, covers `tests` too). The split is not arbitrary:
  pre-commit runs each hook in an isolated environment that does not have the
  package installed, so mypy there cannot resolve `import lab_orchestration` and
  cannot check `tests`. The nox session installs the package (`-e.`), which is
  why it can. Do not "fix" the hook by widening its `files:`. It will fail on
  import.
- **Ruff runs a broad ruleset** (bugbear, pyupgrade, pathlib, pytest-style, and
  more). `T20` (no `print`) is ignored only in `tests/**` and `noxfile.py`.
- **Autofix is a syntax-and-style opinion, never a semantic one.** When a hook
  rewrites a semantically loaded line (a `parametrize` names string, a regex, a
  format string), re-run the tests before trusting it.
- **Do not write commands or config from memory.** Verify against the repo (read
  the file, run `--help`) or against the
  [Scientific Python Development Guide](https://learn.scientific-python.org/development/).

## Repository facts

- **src layout.** The importable package is `src/lab_orchestration/`. Tests
  import it as an installed package, so `uv sync` must have run.
- **The version is derived from git tags** via `hatch-vcs`, which generates
  `src/lab_orchestration/_version.py` at build time. **Never hand-edit a
  version.** Any nox session that installs the package rewrites that file and
  leaves the project venv's metadata stale, so `test_version` fails until
  `uv sync --reinstall-package lab-orchestration`. That is environment drift.
  Never edit the test or the version to make it pass.
- **`py.typed`** marks the package as typed (PEP 561).
- Generated from the
  [`scientific-python/cookie`](https://github.com/scientific-python/cookie)
  template, then trimmed from a library to an application. Do not reintroduce
  library-shaped tooling. `.copier-answers.yml` is Copier-managed, do not edit
  it by hand.
- `.github/workflows/ci.yml`: a quality job (prek, pylint, mypy) and a test
  matrix (Python 3.12 on Ubuntu, Windows and macOS), gated by an `alls-green`
  pass job.

## Design constraints

These are load-bearing. Violating one is a design regression, not a style
disagreement.

- **The engine is workflow-agnostic. qPCR is the reference workflow on top of
  it.** Engine code must not import, name, or special-case qPCR. A capability
  that can only be phrased in qPCR terms belongs in the workflow layer.
- **YAGNI is the tiebreaker.** No abstraction without a present, concrete need.
  Generality is demonstrated by the seam, not by a second implementation.
- **Build order is not workflow order.** The engine is completed and
  independently shippable first. Sample-prep and the analysis tail bolt on
  afterwards and depend on it, never the reverse.
- **Opentrons is a core dependency, and installing everywhere is not importing
  anywhere:** in `src/`, only the sample-prep module and its wiring may import
  `opentrons`. It forces `numpy` below version 2, which is why Python is 3.12
  only: numpy 1.26.4 is the last version 1 release and it does not run on 3.13.
  (ADR 0008)
- **Synthetic data only.** No real or proprietary dataset enters this
  repository, ever. The generator stays a simple parametric curve (sigmoidal +
  baseline + noise; knobs: efficiency, starting quantity, Cq) and does not model
  kinetics mechanistically. Document its assumptions.
- **No hardware.** Everything runs on a laptop against simulated instruments.
- **The engine does not know about the analysis tail.** It emits a persisted run
  record and nothing downstream. Engine code must not import, call, or reference
  analysis, nor build a report. (ADR 0001, ADR 0004)
- **The engine executes against an injected clock.** A direct time or sleep call
  in engine code is a defect. (ADR 0002)
- **Run-record timestamps are logical protocol time**, accumulated from declared
  step durations. Building a timestamp from a wall-clock read is a defect.
  (ADR 0005)
- **The engine orchestrates against an instrument interface, never a concrete
  instrument.** The synthetic reading generator belongs to the workflow. Do not
  abstract the interface past the "no engine change to simulate" requirement.
  (ADR 0003)
- **A step names the instrument that performs it.** The engine holds a name-to-
  instrument mapping and dispatches per step. A step naming an instrument that
  was not supplied fails the run. (ADR 0007)

## Working agreement

- **Surface architecture decisions; do not resolve them silently.** When a task
  forks on a design question, state the fork and its tradeoffs and stop. Present
  the options unranked. Do not mark one as recommended or order them so one
  reads that way. The tradeoffs are the deliverable; the choice is not yours.
- Inside the established design, proceed without asking.
- **Do not propose scope.** Suggestions to add a feature, a second workflow, or
  an abstraction "for later" are out of bounds.
- **This file is the standing contract: if the code contradicts it, the code is
  wrong.** Decisions are recorded in the decision docs and distilled here, each
  constraint citing its ADR. If a constraint blocks you or looks wrong, say so.
  Do not override it.
- **Commits: one logical change each.** If the subject line needs two verbs, it
  should have been two commits.
- **Do not commit or push.** Stage nothing, write no commit messages. Report
  what changed and stop. A deny rule in `.claude/settings.json` enforces this,
  but that file is untracked; a fresh clone has the rule as prose only.
- **Do not report a check as run unless its output is in the reply.** Report
  each one separately; a single line covering several stands for none of them.
- **Division of work.** Louis writes the code that carries design: the state
  machine and its public surface, the engine/workflow boundary, and all tests.
  Claude may write skeletons for these. Signatures, annotations, docstrings
  stating the contract, `NotImplementedError` bodies, but not implementations.
  Claude may write plumbing that carries no design decision: CLI wiring, file
  I/O, the synthetic generator, refactors already decided. All of it is
  reviewed. When unsure which side a piece falls on, ask.

## Project state

`project-state.md` at the repository root (untracked) is the project-management
layer: phase, next step, carry-forwards. It is not documentation and not a
decision doc.

- **Edit it by targeted replacement. Never rewrite it.** Name the exact passage
  you are replacing and stop if it does not match. Report the mismatch rather
  than guessing. Then check the result: list its headers, and count the
  carry-forward list against the number the header claims. A rewrite silently
  drops content that was not in the immediate context. This has happened twice,
  and each time an item vanished with nothing failing.
- **The same rule holds for every file you hand back, this one included.**
- Write an entry only if the session moved something.
- Report the change and stop. Do not commit it.
- **Auto-memory is off** (`"autoMemoryEnabled": false` in
  `.claude/settings.json`). Memory files are authored, not accumulated. Do not
  propose re-enabling it.
