import pytest

from lab_orchestration.sample_prep import LiquidHandler, master_mix_reactions


def test_unrecognised_operation_raises_error() -> None:
    liquid_handler = LiquidHandler({"A1": "S1"}, {"S1": 10.0}, set())
    with pytest.raises(ValueError, match="acquire"):
        liquid_handler.invoke("acquire")


def pipetted_volumes(commands: list[str]) -> dict[tuple[str, str], float]:
    volumes: dict[tuple[str, str], float] = {}
    source = ""
    for command in commands:
        if command.startswith("Aspirating"):
            source = command.split(" from ")[1].split(" at ")[0]
        if command.startswith("Dispensing"):
            destination = command.split(" into ")[1].split(" at ")[0]
            if destination != source:
                key = (source, destination)
                volume = float(command.split(" ")[1])
                volumes[key] = volumes.get(key, 0) + volume
    return volumes


@pytest.mark.parametrize(
    "operation",
    ["prepare_master_mix", "prepare_standards", "distribute_master_mix", "add_sample"],
)
def test_valid_operation_returns_none(operation: str) -> None:
    liquid_handler = LiquidHandler({"A1": "S1"}, {"S1": 10.0}, set())
    assert liquid_handler.invoke(operation) is None


def test_commands_is_not_empty_after_invoking() -> None:
    liquid_handler = LiquidHandler({"A1": "S1"}, {"S1": 10.0}, set())
    liquid_handler.invoke("distribute_master_mix")
    assert liquid_handler.protocol.commands()


def test_vendor_failure_raises_runtime_error() -> None:
    liquid_handler = LiquidHandler(
        {f"{row}{col}": "S1" for row in "ABCDEFGH" for col in range(1, 13)},
        {"S1": 10},
        set(),
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
        LiquidHandler(samples, {}, set())


@pytest.mark.parametrize(
    ("standards", "match"),
    [({"S1": 100.0, "S2": 1.0}, "of S1"), ({"S1": 10.0, "S2": 10.0}, "of water")],
)
def test_dilution_volume_below_pipette_minimum_raises(
    standards: dict[str, float], match: str
) -> None:
    with pytest.raises(ValueError, match=match):
        LiquidHandler({"A1": "S1", "A2": "S2"}, standards, set())


def test_standard_tube_overflow_raises() -> None:
    samples = {"A1": "S1", "D1": "S3"} | {
        f"{row}{col}": "S2" for row in "BC" for col in range(1, 13)
    }
    standards = {"S1": 4.0, "S2": 2, "S3": 1}
    with pytest.raises(ValueError, match="S2 needs"):
        LiquidHandler(samples, standards, set())


def test_loading_sheet_lists_every_tube_and_volume() -> None:
    samples = {
        "A1": "S1",
        "A2": "S1",
        "A3": "U1",
        "A4": "U1",
        "A5": "U1",
        "B1": "S2",
        "B2": "S2",
        "C1": "N1",
        "C2": "N1",
    }
    standards = {"S1": 100.0, "S2": 10.0}
    liquid_handler = LiquidHandler(samples, standards, {"N1"})
    assert liquid_handler.loading_sheet() == [
        ("sample", "A1", "S1", 19.0),
        ("sample", "B1", "S2", None),
        ("sample", "C1", "U1", 11.0),
        ("sample", "D1", "N1", None),
        ("sample", "D6", "water", 104.0),
        ("reagent", "C1", "nuclease free water", 236.0),
        ("reagent", "A1", "reaction buffer", 45.0),
        ("reagent", "A2", "dNTPs", 13.0),
        ("reagent", "A3", "MgCl2", 29.0),
        ("reagent", "A4", "forward primer", 21.0),
        ("reagent", "A5", "reverse primer", 21.0),
        ("reagent", "A6", "fluorescent dye", 25.0),
        ("reagent", "B1", "polymerase", 10.0),
        ("reagent", "D1", "master mix", None),
    ]


def test_protocol_pipettes_expected_volumes() -> None:
    samples = {"A1": "S1", "A2": "S2", "A3": "N1"}
    standards = {"S1": 100.0, "S2": 10.0}
    ntc = {"N1"}
    liquid_handler = LiquidHandler(samples, standards, ntc)
    liquid_handler.invoke("prepare_master_mix")
    liquid_handler.invoke("prepare_standards")
    liquid_handler.invoke("distribute_master_mix")
    liquid_handler.invoke("add_sample")
    actual = pipetted_volumes(liquid_handler.protocol.commands())

    reagents = liquid_handler.reagent_rack
    tubes = liquid_handler.sample_rack
    plate = liquid_handler.plate
    mix = str(reagents["D1"])
    water = str(tubes["D6"])

    expected = {
        (str(reagents["C1"]), mix): 231,
        (str(reagents["A1"]), mix): 40,
        (str(reagents["A2"]), mix): 8,
        (str(reagents["A3"]), mix): 24,
        (str(reagents["A4"]), mix): 16,
        (str(reagents["A5"]), mix): 16,
        (str(reagents["A6"]), mix): 20,
        (str(reagents["B1"]), mix): 5,
        (water, str(tubes["C1"])): 7,
        (water, str(tubes["B1"])): 90,
        (str(tubes["A1"]), str(tubes["B1"])): 10,
        (mix, str(plate["A1"])): 18,
        (mix, str(plate["A2"])): 18,
        (mix, str(plate["A3"])): 18,
        (str(tubes["A1"]), str(plate["A1"])): 2,
        (str(tubes["B1"]), str(plate["A2"])): 2,
        (str(tubes["C1"]), str(plate["A3"])): 2,
    }

    assert actual == pytest.approx(expected)
