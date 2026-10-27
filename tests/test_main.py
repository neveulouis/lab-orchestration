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
        "A1    standard  12.30  10000.00",
        "A2    standard  12.14  10000.00",
        "A3    standard  12.34  10000.00",
        "A4    unknown   14.44  2220.93",
        "A5    unknown   13.94  3128.26",
        "A6    unknown   14.27  2495.63",
        "A7    unknown   14.17  2677.26",
        "B1    standard  15.57  1000.00",
        "B2    standard  16.01  1000.00",
        "B3    standard  15.46  1000.00",
        "B4    unknown   16.72  455.45",
        "B5    unknown   17.02  370.78",
        "B6    unknown   16.69  467.01",
        "B7    unknown   17.19  330.43",
        "C1    standard  18.73  100.00",
        "C2    standard  18.77  100.00",
        "C3    standard  18.88  100.00",
        "C4    unknown   21.94  12.21",
        "C5    unknown   22.32  9.42",
        "C6    unknown   22.02  11.54",
        "C7    unknown   22.14  10.63",
        "D1    standard  22.40  10.00",
        "D2    standard  22.20  10.00",
        "D3    standard  22.26  10.00",
        "D4    unknown   27.43  0.27",
        "D5    unknown   27.32  0.29",
        "D6    unknown   27.50  0.26",
        "D7    unknown   27.17  0.32",
        "E1    standard  25.66  1.00",
        "E2    standard  25.51  1.00",
        "E3    standard  25.46  1.00",
        "F1    standard  28.64  0.10",
        "F2    standard  28.73  0.10",
        "F3    standard  29.01  0.10",
        "G1    standard  32.26  0.01",
        "G2    standard  32.21  0.01",
        "G3    standard  32.32  0.01",
        "H1    NTC       —      —",
        "H2    NTC       —      —",
        "H3    NTC       —      —",
    ]
    assert out.splitlines() == expected
