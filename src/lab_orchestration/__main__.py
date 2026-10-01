"""Command-line entry point: runs a program, writes the run record and computes analyses."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

from pathlib import Path

from lab_orchestration.analysis import analyze_run
from lab_orchestration.engine import Instrument, run_and_report_outcome
from lab_orchestration.qpcr import QPCR_PROGRAM
from lab_orchestration.record import read_record, write_record
from lab_orchestration.run_config import RUN_CONTEXT, SEED
from lab_orchestration.sample_prep import LiquidHandler
from lab_orchestration.thermocycler import Thermocycler

THRESHOLD = 0.1
BASELINE_CYCLES = 5
UNKNOWN_QUANTITY = 250


def main() -> None:
    wells = tuple(RUN_CONTEXT)
    quantities = {
        well: info["quantity"] if info["quantity"] is not None else UNKNOWN_QUANTITY
        for well, info in RUN_CONTEXT.items()
    }
    instruments: Mapping[str, Instrument] = {
        "thermocycler": Thermocycler(wells, quantities, SEED),
        "liquid_handler": LiquidHandler(wells),
    }
    path = Path("run.json")

    outcome = run_and_report_outcome(QPCR_PROGRAM, instruments, SEED, RUN_CONTEXT)
    write_record(outcome, path)
    print(f"Run {outcome.terminal_state}, record produced at {path}")  # noqa: T201

    reread = read_record(path)
    if reread.terminal_state == "completed":
        results = analyze_run(reread, THRESHOLD, BASELINE_CYCLES)

        print(f"{'Well':6}{'Role':<10}{'Cq':<7}{'Quantity'}")  # noqa: T201
        for well, result in results.items():
            cell = "—" if result.cq is None else f"{result.cq:.2f}"
            amount = "—" if result.quantity is None else f"{result.quantity:.2f}"
            print(f"{well:<6}{result.role:<10}{cell:<7}{amount}")  # noqa: T201
    else:
        print(reread.reason)  # noqa: T201


if __name__ == "__main__":
    main()
