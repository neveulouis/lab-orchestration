"""Data-analysis tail: reads events and computes Cq."""

from lab_orchestration.engine import Event


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
