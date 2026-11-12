"""Command-line entry point: runs a program, writes the run record and computes analyses."""

import csv
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
UNKNOWN_QUANTITIES = {"U1": 2500, "U2": 400, "U3": 12, "U4": 0.3}


def main() -> None:
    wells = tuple(RUN_CONTEXT)
    quantities = {
        well: info["quantity"]
        if info["quantity"] is not None
        else UNKNOWN_QUANTITIES[info["sample"]]
        for well, info in RUN_CONTEXT.items()
    }
    samples = {well: info["sample"] for well, info in RUN_CONTEXT.items()}
    standards = {
        info["sample"]: info["quantity"]
        for info in RUN_CONTEXT.values()
        if info["role"] == "standard" and info["quantity"] is not None
    }
    ntcs = {info["sample"] for info in RUN_CONTEXT.values() if info["role"] == "NTC"}
    thermocycler = Thermocycler(wells, quantities, SEED)
    liquid_handler = LiquidHandler(samples, standards, ntcs)
    instruments: Mapping[str, Instrument] = {
        "thermocycler": thermocycler,
        "liquid_handler": liquid_handler,
    }
    sheet_path = Path("loading_sheet.csv")
    path = Path("run.json")

    with sheet_path.open("w", newline="", encoding="utf-8") as sheet_file:
        writer = csv.writer(sheet_file)
        writer.writerow(["rack", "tube", "content", "volume_ul"])
        for rack, tube, content, volume in liquid_handler.loading_sheet():
            volume_cell = "" if volume is None else f"{volume:.2f}"
            writer.writerow([rack, tube, content, volume_cell])
    print(f"Loading sheet produced at {sheet_path}")  # noqa: T201

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
            if result.out_of_range is not None:
                amount = f"{amount} ({result.out_of_range} standard curve range)"
            print(f"{well:<6}{result.role:<10}{cell:<7}{amount}")  # noqa: T201
    else:
        print(reread.reason)  # noqa: T201


if __name__ == "__main__":
    main()
