"""Run configuration: the seed and the plate layout with each well's role and known quantity."""

from typing import TypedDict


class WellInfo(TypedDict):
    "One well's declaration with its role and its known quantity."

    role: str
    quantity: float


SEED = 42

RUN_CONTEXT: dict[str, WellInfo] = {
    "A1": {"role": "standard", "quantity": 1000.0},
    "A2": {"role": "standard", "quantity": 100.0},
    "A3": {"role": "standard", "quantity": 10.0},
}
