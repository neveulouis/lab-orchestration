"""Run record writer and reader: writes and reads the run record."""

import json
from dataclasses import asdict
from pathlib import Path

from lab_orchestration.engine import Event, Outcome


def write_record(outcome: Outcome, path: Path) -> None:
    """Write a json run record from the outcome wherever the caller specifies.

    Writes a json whose top-level keys are Outcome's field names (events,
    terminal_state, reason, seed, run_context).

    Overwrites any record present from previous runs.
    """

    record = asdict(outcome)
    run_json = json.dumps(record, indent=2)
    path.write_text(run_json, encoding="utf-8")


def read_record(path: Path) -> Outcome:
    """Read a json run record from the path specified by the caller into
    an Outcome.

    Reject a malformed run record on terminal state only (ValueError).

    Anything else malformed raises as-is: JSONDecodeError, KeyError or TypeError.
    """

    data = json.loads(path.read_text(encoding="utf-8"))
    events: list[Event] = [Event(**fields) for fields in data["events"]]
    terminal_state = data["terminal_state"]
    if terminal_state not in ("completed", "failed"):
        msg = f"Record at {path} has unknown terminal state: {terminal_state!r}"
        raise ValueError(msg)
    reason = data["reason"]
    seed = data["seed"]
    run_context = data["run_context"]
    return Outcome(events, terminal_state, reason, seed, run_context)
