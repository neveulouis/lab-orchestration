"""Command-line entry point: runs a program and writes the run record."""

from pathlib import Path

from lab_orchestration.engine import run_program
from lab_orchestration.qpcr import QPCR_PROGRAM, Thermocycler
from lab_orchestration.record import write_record


def main() -> None:
    instrument = Thermocycler()
    path = Path("run.json")
    events = run_program(QPCR_PROGRAM, instrument)
    write_record(events, path)
    print(f"Run record produced at {path}")  # noqa: T201


if __name__ == "__main__":
    main()
