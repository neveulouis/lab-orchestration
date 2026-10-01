"""Data-analysis tail: reads events, computes Cq, fits standard curve and quantifies the unknowns in a completed run."""

import math
import statistics
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, cast

from lab_orchestration.engine import Event, Outcome

if TYPE_CHECKING:
    from lab_orchestration.run_config import WellInfo


@dataclass(frozen=True)
class StandardCurve:
    """Line of Cq against log10 quantity, fitted over the standard wells."""

    slope: float
    intercept: float
    r_squared: float


@dataclass(frozen=True)
class WellResult:
    """One well's result (cq and quantity) with its role and an out of range flag."""

    role: Literal["standard", "unknown"]
    cq: float | None
    quantity: float | None
    out_of_range: Literal["above", "below"] | None


def readings(events: list[Event]) -> dict[str, list[float]]:
    """Return every well reading present in cycle order.

    Cycle number is the position in the well list (index 0 is cycle 1)
    because qPCR protocol only produces one reading per cycle per well.
    Protocol with multiple acquisitions per cycle would return wrong cycle
    numbers rather than error.

    The instrument knows the true cycle number but does not publish it
    through invoke. Carrying it would change the seam.
    """
    results: dict[str, list[float]] = {}
    for event in events:
        if event.reading is not None:
            for well, value in event.reading.items():
                results.setdefault(well, []).append(value)

    return results


def cq(fluorescence: list[float], threshold: float) -> float | None:
    """Return the fractional cycle number at fluorescence threshold.

    Linearly interpolated between the first reading at or above the threshold and
    the one before. Returns None when the curve never crosses. Not an error because
    it signifies no amplification.

    Cycles are 1 based, indices are 0-based. The returned value is i + fraction since
    the 0-based indexing and the previous index lookup offsets cancel themselves.
    """
    for i, reading in enumerate(fluorescence[1:], start=1):
        if reading >= threshold:
            fraction = (threshold - fluorescence[i - 1]) / (
                reading - fluorescence[i - 1]
            )
            return i + fraction
    return None


def subtract_baseline(fluorescence: list[float], baseline_cycles: int) -> list[float]:
    """Return the reading with the background baseline subtracted.

    The baseline is the mean of the first baseline_cycles readings taken at the flat
    beginning of the curve. It is then subtracted from the readings."""

    baseline = sum(fluorescence[:baseline_cycles]) / baseline_cycles
    return [reading - baseline for reading in fluorescence]


def fit_standard_curve(standards: list[tuple[float, float]]) -> StandardCurve:
    """Return a standard curve fitted to the standards' (quantity, Cq) pairs.

    Raises statistics.StatisticsError with fewer than two standards, or when all
    share one quantity, because no line fits either. Every quantity must be
    positive (log10 of zero raises ValueError)."""

    quantities = [math.log10(quantity) for quantity, _ in standards]
    cqs = [cq_value for _, cq_value in standards]
    slope, intercept = statistics.linear_regression(quantities, cqs)
    r_squared = (statistics.correlation(quantities, cqs)) ** 2
    return StandardCurve(slope, intercept, r_squared)


def quantify(cq_value: float, curve: StandardCurve) -> float:
    """Return the quantity the standard curve assigns to a Cq value.

    In the units the standards were declared in. A Cq outside the standards'
    range extrapolates the line rather than raising."""

    return 10 ** ((cq_value - curve.intercept) / curve.slope)


def analyze_run(
    outcome: Outcome, threshold: float, baseline_cycles: int
) -> dict[str, WellResult]:
    """Return every well's role, Cq and quantity from a completed run's outcome.

    Fits a standard curve over the standard wells and uses it to quantify the
    unknown wells. Standard wells report the quantity declared in the run
    context, not one recovered from the curve. The dict is in the order
    readings() yields wells. Unknowns outside the standards' Cq range are
    quantified by extrapolation and flagged, not raised.

    Raises ValueError when a standard declares no quantity or never crosses the
    threshold, since no curve can be fit without it.
    """
    # pylint cannot see through cast() and reads the run context as object.
    # pylint: disable=no-member,unsubscriptable-object
    context = cast("dict[str, WellInfo]", outcome.run_context)

    cq_values: dict[str, float | None] = {}
    for well, curve in readings(outcome.events).items():
        cq_values[well] = cq(subtract_baseline(curve, baseline_cycles), threshold)

    standard_pairs: list[tuple[float, float]] = []
    for well, info in context.items():
        if info["role"] == "standard":
            quantity = info["quantity"]
            value = cq_values[well]
            if quantity is None:
                msg = f"Standard {well} declares no quantity"
                raise ValueError(msg)
            if value is None:
                msg = f"Standard {well} never crossed the threshold"
                raise ValueError(msg)
            standard_pairs.append((quantity, value))
    standard_curve = fit_standard_curve(standard_pairs)
    standard_cqs = [cq_value for _, cq_value in standard_pairs]
    lowest_cq, highest_cq = min(standard_cqs), max(standard_cqs)

    results: dict[str, WellResult] = {}
    out_of_range: Literal["above", "below"] | None
    for well, value in cq_values.items():
        info = context[well]
        role = info["role"]
        if role == "standard":
            quantity = info["quantity"]
            out_of_range = None
        elif value is None:
            quantity = None
            out_of_range = None
        else:
            quantity = quantify(value, standard_curve)
            if value < lowest_cq:
                out_of_range = "above"
            elif value > highest_cq:
                out_of_range = "below"
            else:
                out_of_range = None
        results[well] = WellResult(role, value, quantity, out_of_range)

    return results
