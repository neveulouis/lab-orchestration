"""Sample preparation instrument."""

from typing import Literal

import opentrons.simulate

ROBOT_TYPE: Literal["Flex"] = "Flex"
API_LEVEL = "2.29"
MASTER_MIX_VOLUME_UL = 18
SAMPLE_VOLUME_UL = 2
MIXING_VOLUME_UL = 10
MIXING_REPETITIONS = 10


class LiquidHandler:
    """An Opentrons Flex liquid handler that distributes master mix and add sample to a single well"""

    def __init__(self) -> None:
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

    def invoke(self, operation: str) -> float | None:

        if operation == "distribute_master_mix":
            self.pipette.transfer(
                volume=MASTER_MIX_VOLUME_UL,
                source=self.reservoir["A1"],
                dest=self.plate["A1"],
            )
            return None

        if operation == "add_sample":
            self.pipette.transfer(
                volume=SAMPLE_VOLUME_UL,
                source=self.reservoir["A2"],
                dest=self.plate["A1"],
                mix_after=(MIXING_REPETITIONS, MIXING_VOLUME_UL),
            )
            return None

        msg = f"unknown operation: {operation!r}"
        raise ValueError(msg)
