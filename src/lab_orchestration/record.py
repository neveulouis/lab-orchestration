"""Run record writer: writes events as run record json."""

import json
from dataclasses import asdict
from pathlib import Path

from lab_orchestration.engine import Event


def write_record(events: list[Event], path: Path) -> None:
    """Write a json run record from an event list wherever the caller specifies."""

    record = {"events": [asdict(event) for event in events]}
    run_json = json.dumps(record, indent=2)
    path.write_text(run_json, encoding="utf-8")
