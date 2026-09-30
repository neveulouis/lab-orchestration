"""Run configuration: the seed and the plate layout with each well's role and known quantity, if any."""

from typing import Literal, TypedDict


class WellInfo(TypedDict):
    """One well's declaration with its role and its known quantity, if any."""

    role: Literal["standard", "unknown"]
    quantity: float | None


SEED = 42

RUN_CONTEXT: dict[str, WellInfo] = {
    "A1": {"role": "standard", "quantity": 1000.0},
    "A2": {"role": "standard", "quantity": 100.0},
    "A3": {"role": "standard", "quantity": 10.0},
    "A4": {"role": "unknown", "quantity": None},
}
