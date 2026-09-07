from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

from lab_orchestration.engine import Instrument, run_and_report_outcome
from lab_orchestration.qpcr import QPCR_PROGRAM
from lab_orchestration.sample_prep import LiquidHandler
from lab_orchestration.thermocycler import Thermocycler


def test_qpcr_program_runs_to_completion_using_both_instruments() -> None:
    instruments: Mapping[str, Instrument] = {
        "thermocycler": Thermocycler(),
        "liquid_handler": LiquidHandler(),
    }
    outcome = run_and_report_outcome(QPCR_PROGRAM, instruments)
    assert outcome.terminal_state == "completed"
