import json
from pathlib import Path

import pytest

from lab_orchestration.engine import Event, Outcome
from lab_orchestration.record import read_record, write_record


def test_writer_writes_parseable_record(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    outcome = Outcome(
        [
            Event("ramp", 10, None),
            Event("heat", 40, None),
            Event("hold", 55, 6.7),
            Event("stop", 70, None),
        ],
        "completed",
        None,
    )
    write_record(outcome, path)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record == {
        "events": [
            {"operation": "ramp", "timestamp": 10, "reading": None},
            {"operation": "heat", "timestamp": 40, "reading": None},
            {"operation": "hold", "timestamp": 55, "reading": 6.7},
            {"operation": "stop", "timestamp": 70, "reading": None},
        ],
        "terminal_state": "completed",
        "reason": None,
    }


def test_record_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    outcome = Outcome(
        [
            Event("ramp", 10, None),
            Event("heat", 40, None),
            Event("hold", 55, 6.7),
            Event("stop", 70, None),
        ],
        "completed",
        None,
    )
    write_record(outcome, path)
    restored = read_record(path)
    assert restored == outcome


def test_reader_rejects_malformed_terminal_state(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    path.write_text(
        json.dumps({"events": [], "terminal_state": "fish", "reason": None}, indent=2),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="fish"):
        read_record(path)
