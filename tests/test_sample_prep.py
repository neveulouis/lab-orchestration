import pytest

from lab_orchestration.sample_prep import LiquidHandler, master_mix_reactions


def test_unrecognised_operation_raises_error() -> None:
    liquid_handler = LiquidHandler(("A1",))
    with pytest.raises(ValueError, match="acquire"):
        liquid_handler.invoke("acquire")


@pytest.mark.parametrize(
    "operation", ["prepare_master_mix", "distribute_master_mix", "add_sample"]
)
def test_valid_operation_returns_none(operation: str) -> None:
    liquid_handler = LiquidHandler(("A1",))
    assert liquid_handler.invoke(operation) is None


def test_commands_is_not_empty_after_invoking() -> None:
    liquid_handler = LiquidHandler(("A1",))
    liquid_handler.invoke("distribute_master_mix")
    assert liquid_handler.protocol.commands()


def test_vendor_failure_raises_runtime_error() -> None:
    liquid_handler = LiquidHandler(
        tuple(f"{row}{col}" for row in "ABCDEFGH" for col in range(1, 13))
    )
    liquid_handler.invoke("distribute_master_mix")
    with pytest.raises(RuntimeError, match="add_sample"):
        liquid_handler.invoke("add_sample")


@pytest.mark.parametrize(("well_count", "expected"), [(1, 20), (15, 20), (40, 45)])
def test_master_mix_reactions_respect_floor_and_margin(
    well_count: int, expected: int
) -> None:
    assert master_mix_reactions(well_count) == expected
