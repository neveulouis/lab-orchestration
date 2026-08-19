import pytest

from lab_orchestration.engine import (
    Event,
    Program,
    Repeat,
    Step,
    StepFailed,
    run_program,
)


class ComputingInstrument:
    """A stand-in instrument that records what it performed, returns a reading for one operation anf fails on demand."""

    def __init__(self) -> None:
        self.performed: list[str] = []
        self.count: int = 0

    def invoke(self, operation: str) -> float | None:
        self.performed.append(operation)
        if operation == "blast":
            return 42.0
        if operation == "break":
            self.count = self.count + 1
            if self.count == 3:
                msg = "Instrument broke, too many break cycles"
                raise RuntimeError(msg)
        return None


program_cases = pytest.mark.parametrize(
    ("program", "expected"),
    [
        pytest.param(
            [Step("heat", 10), Step("hold", 20), Step("cool", 40)],
            [Event("heat", 10, None), Event("hold", 30, None), Event("cool", 70, None)],
            id="flat",
        ),
        pytest.param(
            [
                Step("ramp", 10),
                Repeat(
                    2,
                    [Step("heat", 30), Repeat(2, [Step("hold", 15)]), Step("cool", 5)],
                ),
                Step("stop", 40),
            ],
            [
                Event("ramp", 10, None),
                Event("heat", 40, None),
                Event("hold", 55, None),
                Event("hold", 70, None),
                Event("cool", 75, None),
                Event("heat", 105, None),
                Event("hold", 120, None),
                Event("hold", 135, None),
                Event("cool", 140, None),
                Event("stop", 180, None),
            ],
            id="nested_repeats",
        ),
        pytest.param(
            [
                Step("ramp", 10),
                Repeat(0, [Step("heat", 30)]),
                Step("stop", 40),
            ],
            [Event("ramp", 10, None), Event("stop", 50, None)],
            id="zero_count",
        ),
    ],
)


@program_cases
def test_event_timestamps_are_cumulative_completion_times(
    program: Program, expected: list[Event]
) -> None:
    events = run_program(program, ComputingInstrument())
    assert events == expected


@program_cases
def test_each_step_invokes_the_instrument_once_in_program_order(
    program: Program, expected: list[Event]
) -> None:
    instrument = ComputingInstrument()
    run_program(program, instrument)
    assert instrument.performed == [event.operation for event in expected]


def test_reading_travels_from_instrument_to_event() -> None:
    instrument = ComputingInstrument()
    program: Program = [Step("heat", 10), Step("blast", 10), Step("cool", 10)]
    events = run_program(program, instrument)
    assert events == [
        Event("heat", 10, None),
        Event("blast", 20, 42.0),
        Event("cool", 30, None),
    ]


def test_failing_step_keeps_the_events_that_completed() -> None:
    instrument = ComputingInstrument()
    program: Program = [Repeat(2, [Repeat(2, [Step("break", 30)])])]
    with pytest.raises(StepFailed) as excinfo:
        run_program(program, instrument)
    assert str(excinfo.value) == "Instrument broke, too many break cycles"
    assert excinfo.value.events == [Event("break", 30, None), Event("break", 60, None)]
