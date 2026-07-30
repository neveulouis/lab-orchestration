"""Command-line entry point: runs a program and prints the trace."""

from lab_orchestration.engine import run_program
from lab_orchestration.qpcr import QPCR_PROGRAM


class RecordingInstrument:
    """A stand-in instrument that remembers what it was asked to perform."""

    def __init__(self) -> None:
        self.performed: list[str] = []

    def invoke(self, operation: str) -> None:
        self.performed.append(operation)


def main() -> None:
    instrument = RecordingInstrument()
    events = run_program(QPCR_PROGRAM, instrument)
    # run_program returns data; printing it belongs here, at the entry point, not inside the engine.
    for event in events:
        print(f"t={event.timestamp}s, {event.operation}")  # noqa: T201


if __name__ == "__main__":
    main()
