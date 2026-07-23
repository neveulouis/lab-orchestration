"""Workflow-agnostic orchestration engine: executes a program and traces what ran."""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class Step:
    label: str
    duration: int


type Program = Sequence[Step | Repeat]


@dataclass
class Repeat:
    count: int
    program: Program


@dataclass
class Event:
    label: str
    timestamp: int


def run_program(program: Program) -> list[Event]:
    """Walk a program in order, looping over repeats, accumulating logical time and emitting one event per step."""

    elapsed = 0
    events = []

    for item in program:
        if isinstance(item, Step):
            elapsed = elapsed + item.duration
            events.append(Event(item.label, elapsed))
        elif isinstance(item, Repeat):
            for _ in range(item.count):
                block_events = run_program(item.program)
                for event in block_events:
                    event.timestamp = elapsed + event.timestamp
                elapsed = block_events[-1].timestamp
                events.extend(block_events)

    return events


if __name__ == "__main__":
    program: Program = [
        Step("initial denaturation", 400),
        Repeat(40, [Step("denature", 30), Step("anneal", 30), Step("extend", 30)]),
        Step("final hold", 120),
    ]
    events = run_program(program)
    # run_program returns data; printing it belongs here, at the entry point, not inside the engine.
    for event in events:
        print(f"t={event.timestamp}s, {event.label}")  # noqa: T201
