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
        self.cycle_number: int = 0

    def invoke(self, operation: str) -> float | None:
        if operation in ("initial_denaturation", "annealing"):
            return None  # recognized but inert operations for this instrument
        if operation == "denaturation":
            self.cycle_number = self.cycle_number + 1
            return None
        if operation == "extension":
            if self.cycle_number == 0:
                msg = "extension invoked before any denaturation. There is no cycle to record a reading against"
                raise RuntimeError(msg)
            return CURVE_PLATEAU / (
                1
                + math.exp(
                    -CURVE_STEEPNESS * (self.cycle_number - CURVE_MIDPOINT_CYCLE)
                )
            )
        msg = f"unknown operation: {operation!r}"
        raise ValueError(msg)
