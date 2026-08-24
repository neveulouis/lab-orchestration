"""Data-analysis tail: reads events and computes cq value"""

from lab_orchestration.engine import Event


def readings(events: list[Event]) -> list[float]:
    """Return every reading present in the events in emission order.

    Cycle number is the position in the list (index 0 is cycle 1) because
    qPCR protocol only produces one reading per cycle. Protocol with multiple
    acquisitions per cycle would return wrong cycle numbers rather than error.

    The instrument knows the true cycle number but only publishes a single
    value through invoke. Carrying it would change the seam.
    """
    return [event.reading for event in events if event.reading is not None]


def cq(fluorescence: list[float], threshold: float) -> float | None:
    """Return the fractional cycle number at which the curve reaches the fluorescence
    threshold.

    Linearly interpolated between the first reading at or above the threshold and
    the one before. Returns None when the curve never crosses not an error because
    it signifies no amplification.

    Cycles are 1 based, indices are 0-based. The returned value is i + fraction since
    the 0-based indexing and the previous index lookup offsets cancel themselves.
    """
    for i, reading in enumerate(fluorescence[1:], start=1):
        if reading >= threshold:
            fraction = (threshold - fluorescence[i - 1]) / (
                fluorescence[i] - fluorescence[i - 1]
            )
            return i + fraction
    return None
