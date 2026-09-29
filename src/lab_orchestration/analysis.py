"""Data-analysis tail: reads events, computes Cq and fits standard curve."""

import math
import statistics
from dataclasses import dataclass

from lab_orchestration.engine import Event


@dataclass(frozen=True)
class StandardCurve:
    """Line of Cq against log10 quantity, fitted over the standard wells."""

    slope: float
    intercept: float
    r_squared: float


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
