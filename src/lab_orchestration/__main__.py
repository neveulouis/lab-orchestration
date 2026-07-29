"""Command-line entry point: runs a program and prints the trace"""

from lab_orchestration.engine import Program, Repeat, Step, run_program


class Toaster:
    """A stand-in instrument that remembers what it was asked to perform."""

    def __init__(self) -> None:
        self.performed: list[str] = []

    def invoke(self, operation: str) -> None:
        self.performed.append(operation)


def main() -> None:
    program: Program = [
        Step("heat", 400),
        Repeat(3, [Step("grill", 30), Step("cool", 30), Step("grill", 30)]),
        Step("stop", 120),
    ]
    instrument = Toaster()
    events = run_program(program, instrument)
    # run_program returns data; printing it belongs here, at the entry point, not inside the engine.
    for event in events:
        print(f"t={event.timestamp}s, {event.operation}")  # noqa: T201
    print(instrument.performed == [event.operation for event in events])  # noqa: T201


if __name__ == "__main__":
    main()
