from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

from lab_orchestration.engine import Instrument, run_and_report_outcome
from lab_orchestration.qpcr import QPCR_PROGRAM
from lab_orchestration.sample_prep import LiquidHandler
from lab_orchestration.thermocycler import Thermocycler


def test_qpcr_program_runs_to_completion_using_both_instruments() -> None:
    instruments: Mapping[str, Instrument] = {
        "thermocycler": Thermocycler(("A1", "A2", "A3")),
        "liquid_handler": LiquidHandler(("A1", "A2", "A3")),
    }
    outcome = run_and_report_outcome(QPCR_PROGRAM, instruments)
    assert outcome.terminal_state == "completed"
    assert outcome.events[-1].reading is not None
    assert len(outcome.events[-1].reading) == 3
