"""Run record writer: writes outcome as run record json."""

import json
from dataclasses import asdict
from pathlib import Path

from lab_orchestration.engine import Outcome


def write_record(outcome: Outcome, path: Path) -> None:
    """Write a json run record from the outcome wherever the caller specifies.

    Writes a json whose top-level keys are Outcome's field names (events,
    terminal_state, reason).

    Overwrites any record present from previous runs.
    """

    record = asdict(outcome)
    run_json = json.dumps(record, indent=2)
    path.write_text(run_json, encoding="utf-8")
