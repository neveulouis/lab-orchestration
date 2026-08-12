"""qPCR workflow definition."""

import math

from lab_orchestration.engine import Program, Repeat, Step

QPCR_PROGRAM: Program = [
    Step("initial_denaturation", 300),
    Repeat(
        40, [Step("denaturation", 15), Step("annealing", 30), Step("extension", 30)]
    ),
]

CURVE_PLATEAU = 1
CURVE_MIDPOINT_CYCLE = 20
CURVE_STEEPNESS = 0.5


class Thermocycler:
    """A simple simulated thermocycler that returns a deterministic fluorescence curve"""

    def __init__(self) -> None:
        self.readings: dict[int, float] = {}
        self.cycle_number: int = 0

    def invoke(self, operation: str) -> None:
        if operation in ("initial_denaturation", "annealing"):
            pass  # recognized but inert operations for this instrument
        elif operation == "denaturation":
            self.cycle_number = self.cycle_number + 1
        elif operation == "extension":
            self.readings[self.cycle_number] = CURVE_PLATEAU / (
                1
                + math.exp(
                    -CURVE_STEEPNESS * (self.cycle_number - CURVE_MIDPOINT_CYCLE)
                )
            )
        else:
            msg = f"unknown operation: {operation!r}"
            raise ValueError(msg)
