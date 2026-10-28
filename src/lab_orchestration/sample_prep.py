"""Sample preparation instrument."""

import logging
from collections.abc import Mapping
from typing import Literal

import opentrons.simulate

ROBOT_TYPE: Literal["Flex"] = "Flex"
API_LEVEL = "2.29"
TOTAL_REACTION_VOLUME_UL = 20
SAMPLE_VOLUME_UL = 2
SAMPLE_MIXING_VOLUME_UL = 10
SAMPLE_MIXING_REPETITIONS = 10
MASTER_MIX_VOLUME_UL = TOTAL_REACTION_VOLUME_UL - SAMPLE_VOLUME_UL

# Pipette and dead volume: the extra reactions cover what is lost in the
# mix tube and on tips.
EXTRA_REACTIONS = 5

# The smallest batch at which polymerase (0.25 uL per reaction) clears the
# Flex 1-channel pipette's 5 uL minimum. The simulator accepts smaller
# volumes silently, so this floor is the only guard.
MINIMUM_REACTIONS = 20

# Per 20 uL reaction: 18 uL master mix + 2 uL template.
REACTION_BUFFER_VOLUME_UL = 2  # 10x stock, 1x final
REACTION_BUFFER_TUBE_POSITION = "A1"
DNTP_VOLUME_UL = 0.4  # 10mM stock, 200uM final
DNTP_TUBE_POSITION = "A2"
MGCL2_VOLUME_UL = 1.2  # 50mM stock, 3mM final
MGCL2_TUBE_POSITION = "A3"
FORWARD_PRIMER_VOLUME_UL = 0.8  # 10 uM stock, 0.4 uM final
FORWARD_PRIMER_TUBE_POSITION = "A4"
REVERSE_PRIMER_VOLUME_UL = 0.8  # 10 uM stock, 0.4 uM final
REVERSE_PRIMER_TUBE_POSITION = "A5"
FLUORESCENT_DYE_VOLUME_UL = 1  # 20x stock, 1x final
FLUORESCENT_DYE_TUBE_POSITION = "A6"
POLYMERASE_VOLUME_UL = 0.25  # 5 U/uL stock, 1.25 U per reaction
POLYMERASE_TUBE_POSITION = "B1"
NUCLEASE_FREE_WATER_VOLUME_UL = MASTER_MIX_VOLUME_UL - (
    REACTION_BUFFER_VOLUME_UL
    + DNTP_VOLUME_UL
    + MGCL2_VOLUME_UL
    + FORWARD_PRIMER_VOLUME_UL
    + REVERSE_PRIMER_VOLUME_UL
    + FLUORESCENT_DYE_VOLUME_UL
    + POLYMERASE_VOLUME_UL
)
NUCLEASE_FREE_WATER_TUBE_POSITION = "C1"
MIXING_TUBE_POSITION = "D1"

# Master mix recipe as (tube, per-reaction volume), in pipetting order.
# Water goes first, polymerase goes last.
MASTER_MIX_RECIPE = (
    (NUCLEASE_FREE_WATER_TUBE_POSITION, NUCLEASE_FREE_WATER_VOLUME_UL),
    (REACTION_BUFFER_TUBE_POSITION, REACTION_BUFFER_VOLUME_UL),
    (DNTP_TUBE_POSITION, DNTP_VOLUME_UL),
    (MGCL2_TUBE_POSITION, MGCL2_VOLUME_UL),
    (FORWARD_PRIMER_TUBE_POSITION, FORWARD_PRIMER_VOLUME_UL),
    (REVERSE_PRIMER_TUBE_POSITION, REVERSE_PRIMER_VOLUME_UL),
    (FLUORESCENT_DYE_TUBE_POSITION, FLUORESCENT_DYE_VOLUME_UL),
    (POLYMERASE_TUBE_POSITION, POLYMERASE_VOLUME_UL),
)

# Rinse each addition out of the tip.
MASTER_MIX_RINSING_VOLUME_UL = 50
MASTER_MIX_RINSING_REPETITIONS = 3
# Homogenise the batch; 150 uL stays under the 200 uL tip and the smallest batch.
MASTER_MIX_FINAL_MIX_VOLUME_UL = 150
MASTER_MIX_FINAL_MIX_REPETITIONS = 10


def master_mix_reactions(well_count: int) -> int:
    """Return how many reactions of master mix to prepare for a plate.

    One reaction per well plus EXTRA_REACTIONS for dead volume, never fewer
    than MINIMUM_REACTIONS, so the smallest component stays pipettable.
    """
    reactions = well_count + EXTRA_REACTIONS
    if reactions < MINIMUM_REACTIONS:
        return MINIMUM_REACTIONS
    return reactions


class LiquidHandler:
    """An Opentrons Flex liquid handler that prepares and distributes master mix and adds sample to a list of wells."""

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
            self.reagent_rack = self.protocol.load_labware(
                load_name="opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap",
                location="C1",
            )
            self.protocol.load_trash_bin(location="A3")
        finally:
            # A failure here would otherwise leave the vendor silenced for the
            # rest of the process.
            vendor_log.setLevel(previous_level)

    def invoke(self, operation: str) -> Mapping[str, float] | None:

        if operation == "prepare_master_mix":
            total_reactions = master_mix_reactions(len(self.wells))
            try:
                for position, volume in MASTER_MIX_RECIPE:
                    self.pipette.transfer(
                        volume=volume * total_reactions,
                        source=self.reagent_rack[position],
                        dest=self.reagent_rack[MIXING_TUBE_POSITION],
                        new_tip="always",
                        mix_after=(
                            MASTER_MIX_RINSING_REPETITIONS,
                            MASTER_MIX_RINSING_VOLUME_UL,
                        ),
                    )
                self.pipette.pick_up_tip()
                self.pipette.mix(
                    MASTER_MIX_FINAL_MIX_REPETITIONS,
                    MASTER_MIX_FINAL_MIX_VOLUME_UL,
                    self.reagent_rack[MIXING_TUBE_POSITION],
                )
                self.pipette.drop_tip()
            except Exception as exc:
                msg = f"{operation} failed: {exc}"
                raise RuntimeError(msg) from exc
            return None

        if operation == "distribute_master_mix":
            try:
                self.pipette.transfer(
                    volume=MASTER_MIX_VOLUME_UL,
                    source=self.reagent_rack[MIXING_TUBE_POSITION],
                    dest=[self.plate[well] for well in self.wells],
                    new_tip="once",
                )
            except Exception as exc:
                msg = f"{operation} failed: {exc}"
                raise RuntimeError(msg) from exc
            return None

        if operation == "add_sample":
            try:
                self.pipette.transfer(
                    volume=SAMPLE_VOLUME_UL,
                    source=self.reservoir["A2"],
                    dest=[self.plate[well] for well in self.wells],
                    new_tip="always",
                    mix_after=(SAMPLE_MIXING_REPETITIONS, SAMPLE_MIXING_VOLUME_UL),
                )
            except Exception as exc:
                msg = f"{operation} failed: {exc}"
                raise RuntimeError(msg) from exc
            return None

        msg = f"unknown operation: {operation!r}"
        raise ValueError(msg)
