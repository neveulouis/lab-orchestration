"""Workflow-agnostic orchestration engine: executes a program and traces what ran."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol


class Instrument(Protocol):
    """An instrument the engine can drive: it accepts an operation by name, performs it and returns a reading if the operation acquires."""

    def invoke(self, operation: str) -> float | None: ...


@dataclass
class Step:
    """A unit of work with a declared operation an instrument performs and a duration."""

    instrument: str
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
    """A step completion output, naming the instrument that performed it, stamped with logical protocol time and data."""

    instrument: str
    operation: str
    timestamp: int
    reading: float | None


@dataclass
class Outcome:
    """A program completion outcome, holding events, terminal state and reason for stopping."""

    events: list[Event]
    terminal_state: Literal["completed", "failed"]
    reason: str | None


class StepFailed(Exception):
    """Raised when a step's invocation fails, carrying the events that completed before it."""

    def __init__(self, events: list[Event], reason: str) -> None:
        self.events: list[Event] = events
        super().__init__(reason)


def run_program(program: Program, instruments: Mapping[str, Instrument]) -> list[Event]:
    """Walk a program in order, looping over repeats, accumulating logical time.

    The instrument the step names is invoked once at every step completion. One event
    is emitted per step, naming that instrument and stamped with that time and the
    reading when the operation acquires. A step naming an instrument that was not
    supplied raises StepFailed before the instrument is invoked.

    Events on a raised StepFailed are already in run time.
    """

    elapsed = 0
    events: list[Event] = []

    for item in program:
        if isinstance(item, Step):
            try:
                instrument = instruments[item.instrument]
            except KeyError as exc:
                msg = f"unknown instrument: {item.instrument!r} at operation: {item.operation!r}"
                raise StepFailed(events, msg) from exc

            elapsed = elapsed + item.duration

            try:
                reading = instrument.invoke(item.operation)
            except (ValueError, RuntimeError) as exc:
                raise StepFailed(events, str(exc)) from exc

            events.append(Event(item.instrument, item.operation, elapsed, reading))

        elif isinstance(item, Repeat):
            for _ in range(item.count):
                try:
                    block_events = run_program(item.program, instruments)
                except StepFailed as exc:
                    for event in exc.events:
                        event.timestamp = elapsed + event.timestamp
                    events.extend(exc.events)
                    raise StepFailed(events, str(exc)) from exc

                for event in block_events:
                    event.timestamp = elapsed + event.timestamp
                elapsed = block_events[-1].timestamp
                events.extend(block_events)

    return events


def run_and_report_outcome(
    program: Program, instruments: Mapping[str, Instrument]
) -> Outcome:
    """Run the program and report outcome catching any failure.

    A failed run returns like any other run. StepFailed does not escape. The caller
    reads terminal_state to tell a completed run from a failed one.

    However a step fails, the run ends the same way.
    """

    try:
        events = run_program(program, instruments)
        return Outcome(events, "completed", None)
    except StepFailed as exc:
        return Outcome(exc.events, "failed", str(exc))
