import pytest

from lab_orchestration.analysis import (
    StandardCurve,
    cq,
    fit_standard_curve,
    quantify,
    readings,
    subtract_baseline,
)
from lab_orchestration.engine import Event

# A noiseless, offset-free logistic curve.
CURVE = [
    7.484622751061123e-05,
    0.00012339457598623172,
    0.00020342697805520653,
    0.0003353501304664781,
    0.0005527786369235996,
    0.0009110511944006454,
    0.0015011822567369917,
    0.0024726231566347743,
    0.004070137715896128,
    0.0066928509242848554,
    0.01098694263059318,
    0.01798620996209156,
    0.02931223075135632,
    0.04742587317756678,
    0.07585818002124355,
    0.11920292202211755,
    0.18242552380635635,
    0.2689414213699951,
    0.3775406687981454,
    0.5,
    0.6224593312018546,
    0.7310585786300049,
    0.8175744761936437,
    0.8807970779778823,
    0.9241418199787566,
    0.9525741268224334,
    0.9706877692486436,
    0.9820137900379085,
    0.9890130573694068,
    0.9933071490757153,
    0.995929862284104,
    0.9975273768433653,
    0.998498817743263,
    0.9990889488055994,
    0.9994472213630764,
    0.9996646498695336,
    0.9997965730219448,
    0.9998766054240137,
    0.9999251537724895,
    0.9999546021312976,
]


def test_readings_are_returned_filtered_and_in_order() -> None:
    events = [
        Event("toaster", "ramp", 10, {"X1": 1.5, "X2": 0.5}),
        Event("toaster", "heat", 40, {"X1": 2.8, "X2": 0.8}),
        Event("toaster", "hold", 55, None),
        Event("toaster", "stop", 65, {"X1": 3.1, "X2": 1.2}),
    ]
    assert readings(events) == {"X1": [1.5, 2.8, 3.1], "X2": [0.5, 0.8, 1.2]}


def test_crossing_returns_expected_cq_value() -> None:
    threshold = 0.1
    # True crossing is ~15.606. Linear interpolation underestimates.
    # ~15.557 is the correct interpolated answer, not a bug.
    assert cq(CURVE, threshold) == pytest.approx(15.55697)


def test_no_crossing_returns_none() -> None:
    threshold = 0.99999999
    assert cq(CURVE, threshold) is None


def test_baseline_gets_subtracted() -> None:
    values = [2.0, 4.0, 10.0, 20.0]
    baseline_cycles = 2
    assert subtract_baseline(values, baseline_cycles) == [-1.0, 1.0, 7.0, 17.0]


def test_fit_recovers_known_line() -> None:
    standards = [(1000.0, 20.04), (100.0, 23.36), (10.0, 26.68)]
    curve = fit_standard_curve(standards)
    assert curve.slope == pytest.approx(-3.32)
    assert curve.intercept == pytest.approx(30.0)
    assert curve.r_squared == pytest.approx(1.0)


def test_quantify_returns_correct_value() -> None:
    curve = StandardCurve(-3.32, 30.0, 1)
    assert quantify(23.36, curve) == pytest.approx(100)
