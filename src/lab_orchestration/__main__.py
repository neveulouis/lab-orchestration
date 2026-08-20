"""Command-line entry point: runs a program and writes the run record."""

from pathlib import Path

from lab_orchestration.engine import run_and_report_outcome
from lab_orchestration.qpcr import QPCR_PROGRAM, Thermocycler
from lab_orchestration.record import write_record


def main() -> None:
    instrument = Thermocycler()
    path = Path("run.json")
    outcome = run_and_report_outcome(QPCR_PROGRAM, instrument)
    write_record(outcome, path)
    print(f"Run {outcome.terminal_state}, record produced at {path}")  # noqa: T201


if __name__ == "__main__":
    main()
