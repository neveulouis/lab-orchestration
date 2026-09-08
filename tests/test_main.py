from pathlib import Path

import pytest

from lab_orchestration.__main__ import main


def test_demo_prints_a_row_per_well(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # main() writes to a relative path, so run it somewhere disposable.
    monkeypatch.chdir(tmp_path)
    main()
    out = capsys.readouterr().out
    # These lines are quoted in the README. Change one, change both.
    expected = [
        "Run completed, record produced at run.json",
        "Well  Cq",
        "A1    15.56",
        "A2    15.56",
        "A3    15.56",
    ]
    assert out.splitlines() == expected
