"""Command-line entry point: runs a program, writes the run record and computes analyses."""

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Mapping

    from lab_orchestration.run_config import WellInfo

from pathlib import Path

from lab_orchestration.analysis import (
    cq,
    fit_standard_curve,
    quantify,
    readings,
    subtract_baseline,
)
from lab_orchestration.engine import Instrument, run_and_report_outcome
from lab_orchestration.qpcr import QPCR_PROGRAM
from lab_orchestration.record import read_record, write_record
from lab_orchestration.run_config import RUN_CONTEXT, SEED
from lab_orchestration.sample_prep import LiquidHandler
from lab_orchestration.thermocycler import Thermocycler

THRESHOLD = 0.1
UNKNOWN_QUANTITY = 250


def main() -> None:
    # pylint cannot see through cast() and reads the record's context as object.
    # pylint: disable=no-member,unsubscriptable-object

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
        context = cast("dict[str, WellInfo]", reread.run_context)
        cq_well_dict: dict[str, float | None] = {}
        for well, curve in readings(reread.events).items():
            value = cq(subtract_baseline(curve, 5), THRESHOLD)
            cq_well_dict[well] = value

        standard_wells = [
            well for well, info in context.items() if info["role"] == "standard"
        ]
        standard_pairs: list[tuple[float, float]] = []
        for well in standard_wells:
            quantity = context[well]["quantity"]
            value = cq_well_dict[well]
            if quantity is None:
                msg = f"Standard {well} declares no quantity"
                raise ValueError(msg)
            if value is None:
                msg = f"Standard {well} never crossed the threshold"
                raise ValueError(msg)
            standard_pairs.append((quantity, value))
        standard_curve = fit_standard_curve(standard_pairs)

        unknown_wells = [
            well for well, info in context.items() if info["role"] == "unknown"
        ]
        unknown_quantities: dict[str, float | None] = {}
        for well in unknown_wells:
            value = cq_well_dict[well]
            unknown_quantities[well] = (
                None if value is None else quantify(value, standard_curve)
            )

        print(f"{'Well':6}{'Role':<10}{'Cq':<7}{'Quantity'}")  # noqa: T201
        for well, value in cq_well_dict.items():
            role = context[well]["role"]
            cell = "—" if value is None else f"{value:.2f}"
            quantity = (
                context[well]["quantity"]
                if role == "standard"
                else unknown_quantities[well]
            )
            amount = "—" if quantity is None else f"{quantity:.2f}"
            print(f"{well:<6}{role:<10}{cell:<7}{amount}")  # noqa: T201
    else:
        print(reread.reason)  # noqa: T201


if __name__ == "__main__":
    main()
