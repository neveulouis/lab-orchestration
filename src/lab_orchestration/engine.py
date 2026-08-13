"""Workflow-agnostic orchestration engine: executes a program and traces what ran."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


class Instrument(Protocol):
    """An instrument the engine can drive: it accepts an operation by name, performs it and returns a reading if the operation acquires."""

    def invoke(self, operation: str) -> float | None: ...


@dataclass
class Step:
    """A unit of work with a declared operation an instrument performs and a duration."""

    operation: str
    duration: int


type Program = Sequence[Step | Repeat]


@dataclass
class Repeat:
    """A block of program executed a fixed number of times. Blocks may include repetition (nesting)."""

    count: int
    program: Program


@dataclass
class Event:
    """A step completion output, stamped with logical protocol time and data."""

    operation: str
    timestamp: int
    reading: float | None


def run_program(program: Program, instrument: Instrument) -> list[Event]:
    """Walk a program in order, looping over repeats, accumulating logical time.

    Instrument is invoked once at every step completion. One event is emitted
    per step, stamped with that time and the reading when the operation acquires.
    """

    elapsed = 0
    events = []

    for item in program:
        if isinstance(item, Step):
            elapsed = elapsed + item.duration
            reading = instrument.invoke(item.operation)
            events.append(Event(item.operation, elapsed, reading))
        elif isinstance(item, Repeat):
            for _ in range(item.count):
                block_events = run_program(item.program, instrument)
                for event in block_events:
                    event.timestamp = elapsed + event.timestamp
                elapsed = block_events[-1].timestamp
                events.extend(block_events)

    return events
