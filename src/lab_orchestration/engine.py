"""Workflow-agnostic orchestration engine: executes a program and traces what ran."""

from dataclasses import dataclass


@dataclass
class Step:
    label: str
    duration: int


@dataclass
class Event:
    label: str
    timestamp: int


def run_program(program: list[Step]) -> list[Event]:
    """Walk a program in order, accumulating logical time and emitting one event per step."""

    total_duration = 0
    events = []

    for step in program:
        total_duration = total_duration + step.duration
        events.append(Event(step.label, total_duration))

    return events


if __name__ == "__main__":
    program = [Step("denature", 30), Step("anneal", 30), Step("extend", 60)]
    events = run_program(program)
    # run_program returns data; printing it belongs here, at the entry point, not inside the engine.
    for event in events:
        print(f"t={event.timestamp}s, {event.label}")  # noqa: T201
