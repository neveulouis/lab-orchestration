import json
from pathlib import Path

from lab_orchestration.engine import Event
from lab_orchestration.record import write_record


def test_writer_writes_parseable_record(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    events = [
        Event("ramp", 10, None),
        Event("heat", 40, None),
        Event("hold", 55, 6.7),
        Event("stop", 70, None),
    ]
    write_record(events, path)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record == {
        "events": [
            {"operation": "ramp", "timestamp": 10, "reading": None},
            {"operation": "heat", "timestamp": 40, "reading": None},
            {"operation": "hold", "timestamp": 55, "reading": 6.7},
            {"operation": "stop", "timestamp": 70, "reading": None},
        ]
    }
