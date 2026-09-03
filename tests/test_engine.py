import pytest

from lab_orchestration.engine import (
    Event,
    Outcome,
    Program,
    Repeat,
    Step,
    StepFailed,
    run_and_report_outcome,
    run_program,
)


class ComputingInstrument:
    """A stand-in instrument that records what it performed, returns a reading for one operation and fails on demand."""

    def __init__(self, break_on: int | None = None) -> None:
        self.performed: list[str] = []
        self.count: int = 0
        self.break_on = break_on

    def invoke(self, operation: str) -> float | None:
        self.performed.append(operation)
        if operation == "blast":
            return 42.0
        if operation == "break":
            self.count = self.count + 1
            if self.count == self.break_on:
                msg = "Instrument broke, too many break cycles"
                raise RuntimeError(msg)
        return None


program_cases = pytest.mark.parametrize(
    ("program", "expected"),
    [
        pytest.param(
            [
                Step("computing_instrument", "heat", 10),
                Step("computing_instrument", "hold", 20),
                Step("computing_instrument", "cool", 40),
            ],
            [
                Event("computing_instrument", "heat", 10, None),
                Event("computing_instrument", "hold", 30, None),
                Event("computing_instrument", "cool", 70, None),
            ],
            id="flat",
        ),
        pytest.param(
            [
                Step("computing_instrument", "ramp", 10),
                Repeat(
                    2,
                    [
                        Step("computing_instrument", "heat", 30),
                        Repeat(2, [Step("computing_instrument", "hold", 15)]),
                        Step("computing_instrument", "cool", 5),
                    ],
                ),
                Step("computing_instrument", "stop", 40),
            ],
            [
                Event("computing_instrument", "ramp", 10, None),
                Event("computing_instrument", "heat", 40, None),
                Event("computing_instrument", "hold", 55, None),
                Event("computing_instrument", "hold", 70, None),
                Event("computing_instrument", "cool", 75, None),
                Event("computing_instrument", "heat", 105, None),
                Event("computing_instrument", "hold", 120, None),
                Event("computing_instrument", "hold", 135, None),
                Event("computing_instrument", "cool", 140, None),
                Event("computing_instrument", "stop", 180, None),
            ],
            id="nested_repeats",
        ),
        pytest.param(
            [
                Step("computing_instrument", "ramp", 10),
                Repeat(0, [Step("computing_instrument", "heat", 30)]),
                Step("computing_instrument", "stop", 40),
            ],
            [
                Event("computing_instrument", "ramp", 10, None),
                Event("computing_instrument", "stop", 50, None),
            ],
            id="zero_count",
        ),
    ],
)


@program_cases
def test_event_timestamps_are_cumulative_completion_times(
    program: Program, expected: list[Event]
) -> None:
    instruments = {"computing_instrument": ComputingInstrument()}
    events = run_program(program, instruments)
    assert events == expected


@program_cases
def test_each_step_invokes_the_instrument_once_in_program_order(
    program: Program, expected: list[Event]
) -> None:
    instruments = {"computing_instrument": ComputingInstrument()}
    run_program(program, instruments)
    assert instruments["computing_instrument"].performed == [
        event.operation for event in expected
    ]


def test_reading_travels_from_instrument_to_event() -> None:
    instruments = {"computing_instrument": ComputingInstrument()}
    program: Program = [
        Step("computing_instrument", "heat", 10),
        Step("computing_instrument", "blast", 10),
        Step("computing_instrument", "cool", 10),
    ]
    events = run_program(program, instruments)
    assert events == [
        Event("computing_instrument", "heat", 10, None),
        Event("computing_instrument", "blast", 20, 42.0),
        Event("computing_instrument", "cool", 30, None),
    ]


def test_failing_step_keeps_the_events_that_completed() -> None:
    instruments = {"computing_instrument": ComputingInstrument(4)}
    program: Program = [
        Repeat(2, [Repeat(2, [Step("computing_instrument", "break", 30)])])
    ]
    with pytest.raises(StepFailed) as excinfo:
        run_program(program, instruments)
    assert str(excinfo.value) == "Instrument broke, too many break cycles"
    assert excinfo.value.events == [
        Event("computing_instrument", "break", 30, None),
        Event("computing_instrument", "break", 60, None),
        Event("computing_instrument", "break", 90, None),
    ]


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        pytest.param(
            [
                Step("computing_instrument", "heat", 10),
                Repeat(3, [Step("computing_instrument", "blast", 10)]),
                Step("computing_instrument", "cool", 10),
            ],
            Outcome(
                [
                    Event("computing_instrument", "heat", 10, None),
                    Event("computing_instrument", "blast", 20, 42.0),
                    Event("computing_instrument", "blast", 30, 42.0),
                    Event("computing_instrument", "blast", 40, 42.0),
                    Event("computing_instrument", "cool", 50, None),
                ],
                "completed",
                None,
            ),
            id="success",
        ),
        pytest.param(
            [Repeat(2, [Repeat(3, [Step("computing_instrument", "break", 30)])])],
            Outcome(
                [
                    Event("computing_instrument", "break", 30, None),
                    Event("computing_instrument", "break", 60, None),
                    Event("computing_instrument", "break", 90, None),
                    Event("computing_instrument", "break", 120, None),
                    Event("computing_instrument", "break", 150, None),
                ],
                "failed",
                "Instrument broke, too many break cycles",
            ),
            id="failure",
        ),
    ],
)
def test_program_reports_outcome(program: Program, expected: Outcome) -> None:
    instruments = {"computing_instrument": ComputingInstrument(6)}
    outcome = run_and_report_outcome(program, instruments)
    assert outcome == expected


def test_each_step_reaches_the_instrument_it_names() -> None:
    instruments = {
        "instrument_1": ComputingInstrument(),
        "instrument_2": ComputingInstrument(),
    }
    program: Program = [
        Step("instrument_1", "heat", 10),
        Step("instrument_2", "hold", 20),
        Step("instrument_1", "cool", 5),
        Step("instrument_2", "stop", 30),
    ]
    events = run_program(program, instruments)
    assert instruments["instrument_1"].performed == ["heat", "cool"]
    assert instruments["instrument_2"].performed == ["hold", "stop"]
    assert events == [
        Event("instrument_1", "heat", 10, None),
        Event("instrument_2", "hold", 30, None),
        Event("instrument_1", "cool", 35, None),
        Event("instrument_2", "stop", 65, None),
    ]


def test_unsupplied_instrument_fails_the_run() -> None:
    instruments = {"computing_instrument": ComputingInstrument()}
    program: Program = [Step("toaster", "heat", 10)]
    outcome = run_and_report_outcome(program, instruments)
    assert outcome.terminal_state == "failed"
    assert outcome.reason is not None
    assert "toaster" in outcome.reason
