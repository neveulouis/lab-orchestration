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
