import statistics

import pytest

from lab_orchestration.thermocycler import (
    CURVE_MIDPOINT_CYCLE,
    CURVE_NOISE_SD,
    CURVE_OFFSET,
    CURVE_PLATEAU,
    Thermocycler,
)


@pytest.mark.parametrize(
    ("operations", "expected"),
    [
        pytest.param(
            [
                "denaturation",
                "extension",
                "denaturation",
                "extension",
                "denaturation",
                "extension",
            ],
            [False, True, False, True, False, True],
            id="mixed",
        ),
        pytest.param(
            ["denaturation", "denaturation", "denaturation"],
            [False, False, False],
            id="denaturation_only",
        ),
        pytest.param(
            [
                "initial_denaturation",
                "denaturation",
                "annealing",
                "extension",
            ],
            [False, False, False, True],
            id="one_full_cycle",
        ),
    ],
)
def test_readings_return_on_extension(
    operations: list[str], expected: list[bool]
) -> None:
    thermocycler = Thermocycler(("A1",), 42)
    readings = [thermocycler.invoke(operation) is not None for operation in operations]
    assert readings == expected


def test_midpoint_reading_centers_on_half_plateau_plus_offset() -> None:
    thermocycler = Thermocycler(("A1",), 42)
    for _ in range(CURVE_MIDPOINT_CYCLE):
        thermocycler.invoke("denaturation")
        reading = thermocycler.invoke("extension")
    assert reading is not None
    assert reading["A1"] == pytest.approx(
        CURVE_PLATEAU / 2 + CURVE_OFFSET, abs=CURVE_NOISE_SD * 5
    )


def test_readings_increase_with_cycle_number() -> None:
    thermocycler = Thermocycler(("A1",), 42)
    readings = []
    midpoint_index = CURVE_MIDPOINT_CYCLE - 1  # cycle n is at index n-1
    for _ in range(CURVE_MIDPOINT_CYCLE + 5):
        thermocycler.invoke("denaturation")
        data = thermocycler.invoke("extension")
        if data is not None:
            readings.append(data["A1"])
    assert (
        readings[midpoint_index - 5]
        < readings[midpoint_index]
        < readings[midpoint_index + 5]
    )


def test_unrecognised_operation_raises_error() -> None:
    thermocycler = Thermocycler(("A1",), 42)
    with pytest.raises(ValueError, match="acquire"):
        thermocycler.invoke("acquire")


def test_substring_of_recognised_operation_raises_error() -> None:
    thermocycler = Thermocycler(("A1",), 42)
    with pytest.raises(ValueError, match="nat"):
        thermocycler.invoke("nat")


def test_extension_at_cycle_0_raises_error() -> None:
    thermocycler = Thermocycler(("A1",), 42)
    with pytest.raises(RuntimeError, match="before any denaturation"):
        thermocycler.invoke("extension")


def test_multiple_wells_return_multiple_keys_and_a_distinct_value_per_well() -> None:
    thermocycler = Thermocycler(("A1", "A2", "A3"), 42)
    thermocycler.invoke("denaturation")
    reading = thermocycler.invoke("extension")
    assert reading is not None
    assert set(reading.keys()) == {"A1", "A2", "A3"}
    assert len(set(reading.values())) == 3


def test_same_seed_returns_identical_readings() -> None:
    thermocycler_a = Thermocycler(("A1", "A2", "A3"), 42)
    thermocycler_b = Thermocycler(("A1", "A2", "A3"), 42)
    thermocycler_a.invoke("denaturation")
    thermocycler_b.invoke("denaturation")
    reading_a = thermocycler_a.invoke("extension")
    reading_b = thermocycler_b.invoke("extension")
    assert reading_a == reading_b


def test_different_seed_returns_different_readings() -> None:
    thermocycler_a = Thermocycler(("A1", "A2", "A3"), 42)
    thermocycler_b = Thermocycler(("A1", "A2", "A3"), 43)
    thermocycler_a.invoke("denaturation")
    thermocycler_b.invoke("denaturation")
    reading_a = thermocycler_a.invoke("extension")
    reading_b = thermocycler_b.invoke("extension")
    assert reading_a != reading_b


def test_residuals_match_noise_sd() -> None:
    thermocycler = Thermocycler(tuple(f"A{i}" for i in range(1000)), 42)
    thermocycler.invoke("denaturation")
    readings = thermocycler.invoke("extension")
    assert readings is not None
    spread = statistics.stdev(readings.values())
    assert spread == pytest.approx(CURVE_NOISE_SD, rel=0.1)
