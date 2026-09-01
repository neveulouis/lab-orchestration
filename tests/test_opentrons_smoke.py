from typing import Literal

import opentrons.simulate
from opentrons import protocol_api

ROBOT_TYPE: Literal["Flex"] = "Flex"
API_LEVEL = "2.29"


# protocol run function
def run(protocol: protocol_api.ProtocolContext) -> None:
    # labware
    tiprack = protocol.load_labware("opentrons_flex_96_tiprack_200ul", location="D1")
    protocol.load_trash_bin(location="A3")

    # pipettes
    left_pipette = protocol.load_instrument(
        "flex_1channel_1000", mount="left", tip_racks=[tiprack]
    )

    # commands
    left_pipette.pick_up_tip()
    left_pipette.drop_tip()


def test_smoke() -> None:
    protocol = opentrons.simulate.get_protocol_api(API_LEVEL, robot_type=ROBOT_TYPE)
    run(protocol)
    assert protocol.commands()
