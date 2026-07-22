from lab_orchestration.engine import Event, Step, run_program


def test_event_timestamps_are_cumulative_completion_times() -> None:
    program = [Step("start", 10), Step("wait", 20), Step("stop", 40)]
    events = run_program(program)
    assert events == [Event("start", 10), Event("wait", 30), Event("stop", 70)]
