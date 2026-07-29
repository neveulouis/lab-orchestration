import pytest

from lab_orchestration.engine import Event, Program, Repeat, Step, run_program


class RecordingInstrument:
    """A stand-in instrument that remembers what it was asked to perform."""

    def __init__(self) -> None:
        self.performed: list[str] = []

    def invoke(self, operation: str) -> None:
        self.performed.append(operation)


program_cases = pytest.mark.parametrize(
    ("program", "expected"),
    [
        pytest.param(
            [Step("heat", 10), Step("hold", 20), Step("cool", 40)],
            [Event("heat", 10), Event("hold", 30), Event("cool", 70)],
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
                Event("ramp", 10),
                Event("heat", 40),
                Event("hold", 55),
                Event("hold", 70),
                Event("cool", 75),
                Event("heat", 105),
                Event("hold", 120),
                Event("hold", 135),
                Event("cool", 140),
                Event("stop", 180),
            ],
            id="nested_repeats",
        ),
        pytest.param(
            [
                Step("ramp", 10),
                Repeat(0, [Step("heat", 30)]),
                Step("stop", 40),
            ],
            [Event("ramp", 10), Event("stop", 50)],
            id="zero_count",
        ),
    ],
)


@program_cases
def test_event_timestamps_are_cumulative_completion_times(
    program: Program, expected: list[Event]
) -> None:
    events = run_program(program, RecordingInstrument())
    assert events == expected


@program_cases
def test_each_step_invokes_the_instrument_once_in_program_order(
    program: Program, expected: list[Event]
) -> None:
    recorder = RecordingInstrument()
    run_program(program, recorder)
    assert recorder.performed == [event.operation for event in expected]
