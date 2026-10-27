import pytest

from lab_orchestration.sample_prep import LiquidHandler


def test_unrecognised_operation_raises_error() -> None:
    liquid_handler = LiquidHandler(("A1",))
    with pytest.raises(ValueError, match="acquire"):
        liquid_handler.invoke("acquire")


@pytest.mark.parametrize("operation", ["distribute_master_mix", "add_sample"])
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
