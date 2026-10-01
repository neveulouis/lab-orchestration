"""Thermocycler instrument and its synthetic fluorescence curve."""

import math
from collections.abc import Mapping

import numpy as np

CURVE_PLATEAU = 1
CYCLES_PER_10X_DILUTION = 3.32  # log2(10): a 10x dilution delays by 3.32 cyclesassuming perfect doubling each cycle (100% efficiency).
LOWEST_CONCENTRATION_CYCLE = 30
CURVE_STEEPNESS = 0.5
CURVE_OFFSET = 0.05
CURVE_NOISE_SD = 0.01


class Thermocycler:
    """A simple simulated thermocycler that returns a noisy deterministic fluorescence curve"""

    def __init__(
        self, wells: tuple[str, ...], quantities: Mapping[str, float], seed: int
    ) -> None:
        self.cycle_number: int = 0
        self.wells = wells
        self.quantities = quantities
        self.rng = np.random.default_rng(seed)

    def _signal(self, cycle: int, quantity: float) -> float:

        return CURVE_OFFSET + (
            CURVE_PLATEAU
            / (
                1
                + math.exp(
                    -CURVE_STEEPNESS
                    * (
                        cycle
                        - (
                            LOWEST_CONCENTRATION_CYCLE
                            - CYCLES_PER_10X_DILUTION * math.log10(quantity)
                        )
                    )
                )
            )
        )

    def invoke(self, operation: str) -> Mapping[str, float] | None:
        if operation in ("initial_denaturation", "annealing"):
            return None  # recognized but inert operations for this instrument

        if operation == "denaturation":
            self.cycle_number = self.cycle_number + 1
            return None

        if operation == "extension":
            if self.cycle_number == 0:
                msg = "extension invoked before any denaturation. There is no cycle to record a reading against"
                raise RuntimeError(msg)
            return {
                well: float(
                    self._signal(self.cycle_number, self.quantities[well])
                    + self.rng.normal(0.0, CURVE_NOISE_SD)
                )
                for well in self.wells
            }

        msg = f"unknown operation: {operation!r}"
        raise ValueError(msg)
