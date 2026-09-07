"""Command-line entry point: runs a program and writes the run record."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

from pathlib import Path

from lab_orchestration.analysis import cq, readings
from lab_orchestration.engine import Instrument, run_and_report_outcome
from lab_orchestration.qpcr import QPCR_PROGRAM
from lab_orchestration.record import read_record, write_record
from lab_orchestration.sample_prep import LiquidHandler
from lab_orchestration.thermocycler import Thermocycler

THRESHOLD = 0.1


def main() -> None:
    instruments: Mapping[str, Instrument] = {
        "thermocycler": Thermocycler(),
        "liquid_handler": LiquidHandler(),
    }
    path = Path("run.json")
    outcome = run_and_report_outcome(QPCR_PROGRAM, instruments)
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
