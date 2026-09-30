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
        "Well  Role      Cq     Quantity",
        "A1    standard  15.91  1000.00",
        "A2    standard  18.72  100.00",
        "A3    standard  22.38  10.00",
        "A4    unknown   17.87  224.53",
    ]
    assert out.splitlines() == expected
