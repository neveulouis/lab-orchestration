"""Sample preparation instrument."""

import logging
from collections.abc import Mapping
from typing import Literal

import opentrons.simulate

ROBOT_TYPE: Literal["Flex"] = "Flex"
API_LEVEL = "2.29"
MASTER_MIX_VOLUME_UL = 18
SAMPLE_VOLUME_UL = 2
MIXING_VOLUME_UL = 10
MIXING_REPETITIONS = 10


class LiquidHandler:
    """An Opentrons Flex liquid handler that distributes master mix and adds sample to a list of wells"""

    def __init__(self, wells: tuple[str, ...]) -> None:
        # The vendor logs two warnings while building a context: no
        # robot_settings.json and no belt calibration. Both are permanent on a
        # machine with no Flex attached, so they say nothing a run needs to
        # hear. Quiet only for construction.
        self.wells = wells
        vendor_log = logging.getLogger("opentrons")
        previous_level = vendor_log.level
        vendor_log.setLevel(logging.ERROR)
        try:
            self.protocol = opentrons.simulate.get_protocol_api(
                API_LEVEL, robot_type=ROBOT_TYPE
            )
            tiprack = self.protocol.load_labware(
                "opentrons_flex_96_tiprack_200ul", location="D3"
            )
            self.pipette = self.protocol.load_instrument(
                "flex_1channel_1000", mount="left", tip_racks=[tiprack]
            )
            self.plate = self.protocol.load_labware(
                load_name="corning_96_wellplate_360ul_flat", location="D2"
            )
            self.reservoir = self.protocol.load_labware(
                load_name="usascientific_12_reservoir_22ml", location="D1"
            )
            self.protocol.load_trash_bin(location="A3")
        finally:
            # A failure here would otherwise leave the vendor silenced for the
            # rest of the process.
            vendor_log.setLevel(previous_level)

    def invoke(self, operation: str) -> Mapping[str, float] | None:

        if operation == "distribute_master_mix":
            self.pipette.transfer(
                volume=MASTER_MIX_VOLUME_UL,
                source=self.reservoir["A1"],
                dest=[self.plate[well] for well in self.wells],
                new_tip="once",
            )
            return None

        if operation == "add_sample":
            self.pipette.transfer(
                volume=SAMPLE_VOLUME_UL,
                source=self.reservoir["A2"],
                dest=[self.plate[well] for well in self.wells],
                new_tip="always",
                mix_after=(MIXING_REPETITIONS, MIXING_VOLUME_UL),
            )
            return None

        msg = f"unknown operation: {operation!r}"
        raise ValueError(msg)
