import pytest

from lab_orchestration.sample_prep import LiquidHandler, master_mix_reactions


def test_unrecognised_operation_raises_error() -> None:
    liquid_handler = LiquidHandler({"A1": "S1"}, {"S1": 10.0})
    with pytest.raises(ValueError, match="acquire"):
        liquid_handler.invoke("acquire")


@pytest.mark.parametrize(
    "operation",
    ["prepare_master_mix", "prepare_standards", "distribute_master_mix", "add_sample"],
)
def test_valid_operation_returns_none(operation: str) -> None:
    liquid_handler = LiquidHandler({"A1": "S1"}, {"S1": 10.0})
    assert liquid_handler.invoke(operation) is None


def test_commands_is_not_empty_after_invoking() -> None:
    liquid_handler = LiquidHandler({"A1": "S1"}, {"S1": 10.0})
    liquid_handler.invoke("distribute_master_mix")
    assert liquid_handler.protocol.commands()


def test_vendor_failure_raises_runtime_error() -> None:
    liquid_handler = LiquidHandler(
        {f"{row}{col}": "S1" for row in "ABCDEFGH" for col in range(1, 13)}, {"S1": 10}
    )
    liquid_handler.invoke("distribute_master_mix")
    with pytest.raises(RuntimeError, match="add_sample"):
        liquid_handler.invoke("add_sample")


@pytest.mark.parametrize(("well_count", "expected"), [(1, 20), (15, 20), (40, 45)])
def test_master_mix_reactions_respect_floor_and_margin(
    well_count: int, expected: int
) -> None:
    assert master_mix_reactions(well_count) == expected


def test_more_samples_than_tubes_raises() -> None:
    wells = [f"{row}{col}" for row in "AB" for col in range(1, 13)]
    samples = {well: f"S{i}" for i, well in enumerate(wells)}
    with pytest.raises(ValueError, match="24"):
        LiquidHandler(samples, {})


@pytest.mark.parametrize(
    ("standards", "match"),
    [({"S1": 100.0, "S2": 1.0}, "of S1"), ({"S1": 10.0, "S2": 10.0}, "of water")],
)
def test_dilution_volume_below_pipette_minimum_raises(
    standards: dict[str, float], match: str
) -> None:
    with pytest.raises(ValueError, match=match):
        LiquidHandler({"A1": "S1", "A2": "S2"}, standards)


def test_standard_tube_overflow_raises() -> None:
    samples = {"A1": "S1", "D1": "S3"} | {
        f"{row}{col}": "S2" for row in "BC" for col in range(1, 13)
    }
    standards = {"S1": 4.0, "S2": 2, "S3": 1}
    with pytest.raises(ValueError, match="S2 needs"):
        LiquidHandler(samples, standards)
