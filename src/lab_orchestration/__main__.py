"""Command-line entry point: runs a program and writes the run record."""

from pathlib import Path

from lab_orchestration.analysis import cq, readings
from lab_orchestration.engine import run_and_report_outcome
from lab_orchestration.qpcr import QPCR_PROGRAM, Thermocycler
from lab_orchestration.record import read_record, write_record

THRESHOLD = 0.1


def main() -> None:
    instrument = Thermocycler()
    path = Path("run.json")
    outcome = run_and_report_outcome(QPCR_PROGRAM, instrument)
    write_record(outcome, path)
    print(f"Run {outcome.terminal_state}, record produced at {path}")  # noqa: T201
    reread = read_record(path)
    if reread.terminal_state == "completed":
        value = cq(readings(reread.events), THRESHOLD)
        if value is None:
            print("No amplification detected")  # noqa: T201
        else:
            print(f"Cq: {value:.2f}")  # noqa: T201
    else:
        print(reread.reason)  # noqa: T201


if __name__ == "__main__":
    main()
