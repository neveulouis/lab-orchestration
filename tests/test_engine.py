import pytest

from lab_orchestration.engine import Event, Program, Repeat, Step, run_program


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        pytest.param(
            [Step("start", 10), Step("wait", 20), Step("stop", 40)],
            [Event("start", 10), Event("wait", 30), Event("stop", 70)],
            id="flat",
        ),
        pytest.param(
            [
                Step("initial start", 10),
                Repeat(
                    2,
                    [Step("start", 30), Repeat(2, [Step("wait", 15)]), Step("stop", 5)],
                ),
                Step("final stop", 40),
            ],
            [
                Event("initial start", 10),
                Event("start", 40),
                Event("wait", 55),
                Event("wait", 70),
                Event("stop", 75),
                Event("start", 105),
                Event("wait", 120),
                Event("wait", 135),
                Event("stop", 140),
                Event("final stop", 180),
            ],
            id="nested_repeats",
        ),
        pytest.param(
            [
                Step("initial start", 10),
                Repeat(0, [Step("start", 30)]),
                Step("final stop", 40),
            ],
            [Event("initial start", 10), Event("final stop", 50)],
            id="zero_count",
        ),
    ],
)
def test_event_timestamps_are_cumulative_completion_times(
    program: Program, expected: list[Event]
) -> None:
    events = run_program(program)
    assert events == expected
