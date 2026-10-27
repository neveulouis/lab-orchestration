"""Run configuration: the seed and the plate layout with each well's role, known quantity (if any) and its sample name."""

from typing import Literal, TypedDict


class WellInfo(TypedDict):
    """One well's declaration with its role, its known quantity (if any) and its sample name."""

    role: Literal["standard", "NTC", "unknown"]
    quantity: float | None
    sample: str


SEED = 42

RUN_CONTEXT: dict[str, WellInfo] = {
    "A1": {"role": "standard", "quantity": 10000.0, "sample": "S1"},
    "A2": {"role": "standard", "quantity": 10000.0, "sample": "S1"},
    "A3": {"role": "standard", "quantity": 10000.0, "sample": "S1"},
    "A4": {"role": "unknown", "quantity": None, "sample": "U1"},
    "A5": {"role": "unknown", "quantity": None, "sample": "U1"},
    "A6": {"role": "unknown", "quantity": None, "sample": "U1"},
    "A7": {"role": "unknown", "quantity": None, "sample": "U1"},
    "B1": {"role": "standard", "quantity": 1000.0, "sample": "S2"},
    "B2": {"role": "standard", "quantity": 1000.0, "sample": "S2"},
    "B3": {"role": "standard", "quantity": 1000.0, "sample": "S2"},
    "B4": {"role": "unknown", "quantity": None, "sample": "U2"},
    "B5": {"role": "unknown", "quantity": None, "sample": "U2"},
    "B6": {"role": "unknown", "quantity": None, "sample": "U2"},
    "B7": {"role": "unknown", "quantity": None, "sample": "U2"},
    "C1": {"role": "standard", "quantity": 100.0, "sample": "S3"},
    "C2": {"role": "standard", "quantity": 100.0, "sample": "S3"},
    "C3": {"role": "standard", "quantity": 100.0, "sample": "S3"},
    "C4": {"role": "unknown", "quantity": None, "sample": "U3"},
    "C5": {"role": "unknown", "quantity": None, "sample": "U3"},
    "C6": {"role": "unknown", "quantity": None, "sample": "U3"},
    "C7": {"role": "unknown", "quantity": None, "sample": "U3"},
    "D1": {"role": "standard", "quantity": 10.0, "sample": "S4"},
    "D2": {"role": "standard", "quantity": 10.0, "sample": "S4"},
    "D3": {"role": "standard", "quantity": 10.0, "sample": "S4"},
    "D4": {"role": "unknown", "quantity": None, "sample": "U4"},
    "D5": {"role": "unknown", "quantity": None, "sample": "U4"},
    "D6": {"role": "unknown", "quantity": None, "sample": "U4"},
    "D7": {"role": "unknown", "quantity": None, "sample": "U4"},
    "E1": {"role": "standard", "quantity": 1.0, "sample": "S5"},
    "E2": {"role": "standard", "quantity": 1.0, "sample": "S5"},
    "E3": {"role": "standard", "quantity": 1.0, "sample": "S5"},
    "F1": {"role": "standard", "quantity": 0.1, "sample": "S6"},
    "F2": {"role": "standard", "quantity": 0.1, "sample": "S6"},
    "F3": {"role": "standard", "quantity": 0.1, "sample": "S6"},
    "G1": {"role": "standard", "quantity": 0.01, "sample": "S7"},
    "G2": {"role": "standard", "quantity": 0.01, "sample": "S7"},
    "G3": {"role": "standard", "quantity": 0.01, "sample": "S7"},
    "H1": {"role": "NTC", "quantity": 0.0, "sample": "N1"},
    "H2": {"role": "NTC", "quantity": 0.0, "sample": "N1"},
    "H3": {"role": "NTC", "quantity": 0.0, "sample": "N1"},
}
