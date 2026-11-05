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
SAMPLE_NUCLEASE_FREE_WATER_TUBE_POSITION = "D6"
MASTER_MIX_VOLUME_UL = TOTAL_REACTION_VOLUME_UL - SAMPLE_VOLUME_UL

# Pipette and dead volume: the extra reactions cover what is lost in the
# mix tube and on tips.
EXTRA_REACTIONS = 5

# Dead volume left in a 2 mL tube.
TUBE_DEAD_VOLUME_UL = 5

# The smallest batch at which polymerase (0.25 uL per reaction) clears the
# Flex 1-channel 1000 pipette's 5 uL minimum. The simulator accepts smaller
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

# Master mix recipe as (reagent name, tube, per-reaction volume), in
# pipetting order. Water goes first, polymerase goes last.
MASTER_MIX_RECIPE = (
    (
        "nuclease free water",
        NUCLEASE_FREE_WATER_TUBE_POSITION,
        NUCLEASE_FREE_WATER_VOLUME_UL,
    ),
    ("reaction buffer", REACTION_BUFFER_TUBE_POSITION, REACTION_BUFFER_VOLUME_UL),
    ("dNTPs", DNTP_TUBE_POSITION, DNTP_VOLUME_UL),
    ("MgCl2", MGCL2_TUBE_POSITION, MGCL2_VOLUME_UL),
    ("forward primer", FORWARD_PRIMER_TUBE_POSITION, FORWARD_PRIMER_VOLUME_UL),
    ("reverse primer", REVERSE_PRIMER_TUBE_POSITION, REVERSE_PRIMER_VOLUME_UL),
    ("fluorescent dye", FLUORESCENT_DYE_TUBE_POSITION, FLUORESCENT_DYE_VOLUME_UL),
    ("polymerase", POLYMERASE_TUBE_POSITION, POLYMERASE_VOLUME_UL),
)

# Rinse each addition out of the tip.
MASTER_MIX_RINSING_VOLUME_UL = 50
MASTER_MIX_RINSING_REPETITIONS = 3
# Homogenise the batch; 150 uL stays under the 200 uL tip and the smallest batch.
MASTER_MIX_FINAL_MIX_VOLUME_UL = 150
MASTER_MIX_FINAL_MIX_REPETITIONS = 10

# Each lower standard's tube is made up to this total: the transfer is the
# total divided by the fold, the rest is water. At 100 uL the transfer stays
# at or above the 50 pipette's 5 uL minimum up to a 1:20 step.
TOTAL_DILUTION_VOLUME_UL = 100
DILUTION_MIXING_VOLUME_UL = 40
DILUTION_MIXING_REPETITIONS = 10


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
    """An Opentrons Flex liquid handler that prepares master mix and a standard series and loads the plate.

    Sample tubes are assigned in the sample rack's order: standards first,
    highest quantity first, then the other samples in the order they appear.
    D6 holds water. The operator places the top standard; each lower one is
    diluted from the one above it. Raises ValueError if the samples outnumber
    the free tubes, if a dilution volume falls below the pipette's minimum,
    or if a standard's tube cannot cover its replicates and onward transfer.
    """

    def __init__(
        self, samples: Mapping[str, str], standards: Mapping[str, float]
    ) -> None:

        self.samples = samples
        self.standards = standards

        # The vendor logs two warnings while building a context: no
        # robot_settings.json and no belt calibration. Both are permanent on a
        # machine with no Flex attached, so they say nothing a run needs to
        # hear. Quiet only for construction.
        vendor_log = logging.getLogger("opentrons")
        previous_level = vendor_log.level
        vendor_log.setLevel(logging.ERROR)

        try:
            self.protocol = opentrons.simulate.get_protocol_api(
                API_LEVEL, robot_type=ROBOT_TYPE
            )
            tiprack_200 = self.protocol.load_labware(
                "opentrons_flex_96_filtertiprack_200ul", location="D3"
            )
            self.pipette_1000 = self.protocol.load_instrument(
                "flex_1channel_1000", mount="left", tip_racks=[tiprack_200]
            )
            tiprack_50 = self.protocol.load_labware(
                "opentrons_flex_96_filtertiprack_50ul", location="C3"
            )
            self.pipette_50 = self.protocol.load_instrument(
                "flex_1channel_50", mount="right", tip_racks=[tiprack_50]
            )
            self.plate = self.protocol.load_labware(
                load_name="corning_96_wellplate_360ul_flat", location="D2"
            )
            self.reagent_rack = self.protocol.load_labware(
                load_name="opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap",
                location="C1",
            )
            self.sample_rack = self.protocol.load_labware(
                load_name="opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap",
                location="C2",
            )
            self.protocol.load_trash_bin(location="A3")
        finally:
            # A failure here would otherwise leave the vendor silenced for the
            # rest of the process.
            vendor_log.setLevel(previous_level)

        self.standard_series = sorted(
            self.standards, key=lambda name: self.standards[name], reverse=True
        )

        names = self.standard_series + [
            unique_name
            for unique_name in dict.fromkeys(self.samples.values())
            if unique_name not in self.standards
        ]
        free_tubes = [
            tube
            for tube in self.sample_rack.wells()
            if tube.well_name != SAMPLE_NUCLEASE_FREE_WATER_TUBE_POSITION
        ]
        if len(names) > len(free_tubes):
            msg = f"{len(names)} samples but only {len(free_tubes)} free tubes in the sample rack"
            raise ValueError(msg)
        self.sample_tubes = dict(zip(names, free_tubes, strict=False))

        # receiving standard -> (source standard, transfer uL, water uL)
        self.dilution_plan = {}
        for source, receiving in zip(
            self.standard_series, self.standard_series[1:], strict=False
        ):
            fold = self.standards[source] / self.standards[receiving]
            transfer_volume_ul = TOTAL_DILUTION_VOLUME_UL / fold
            water_volume_ul = TOTAL_DILUTION_VOLUME_UL - transfer_volume_ul

            if transfer_volume_ul < self.pipette_50.min_volume:
                msg = (
                    f"diluting {source} into {receiving} needs {transfer_volume_ul:.2f} uL "
                    f"of {source}, below the pipette's {self.pipette_50.min_volume} uL minimum"
                )
                raise ValueError(msg)
            if water_volume_ul < self.pipette_50.min_volume:
                msg = (
                    f"diluting {source} into {receiving} needs {water_volume_ul:.2f} uL "
                    f"of water, below the pipette's {self.pipette_50.min_volume} uL minimum"
                )
                raise ValueError(msg)

            self.dilution_plan[receiving] = (
                source,
                transfer_volume_ul,
                water_volume_ul,
            )

        # Each tube the robot makes must cover its replicate wells, the margin, and
        # what it gives the next standard, as the source of the next pair. The bottom
        # standard gives nothing onward. The top standard is the operator's stock and
        # is not checked here.
        self.onward_transfers = {
            source: transfer_volume_ul
            for source, transfer_volume_ul, _ in self.dilution_plan.values()
        }
        for receiving in self.dilution_plan:
            onward_ul = self.onward_transfers.get(receiving, 0)
            replicates = list(self.samples.values()).count(receiving)
            needed_ul = replicates * SAMPLE_VOLUME_UL + onward_ul + TUBE_DEAD_VOLUME_UL
            if needed_ul > TOTAL_DILUTION_VOLUME_UL:
                msg = (
                    f"{receiving} needs {needed_ul:.2f} uL for its replicates, margin "
                    f"and onward transfer, more than the {TOTAL_DILUTION_VOLUME_UL} uL in its tube"
                )
                raise ValueError(msg)

    def loading_sheet(self) -> list[tuple[str, str, str, float | None]]:

        loading_list = []
        for name, tube in self.sample_tubes.items():
            if name in self.dilution_plan:
                volume = None
            else:
                replicates = list(self.samples.values()).count(name)
                volume = (
                    SAMPLE_VOLUME_UL * replicates
                    + self.onward_transfers.get(name, 0)
                    + TUBE_DEAD_VOLUME_UL
                )
            loading_list.append(("sample", tube.well_name, name, volume))

        water_ul = (
            sum(
                water_volume_ul for _, _, water_volume_ul in self.dilution_plan.values()
            )
            + TUBE_DEAD_VOLUME_UL
        )

        loading_list.append(
            ("sample", SAMPLE_NUCLEASE_FREE_WATER_TUBE_POSITION, "water", water_ul)
        )

        for reagent_name, reagent_position, reagent_volume in MASTER_MIX_RECIPE:
            volume = (
                reagent_volume * master_mix_reactions(len(self.samples))
                + TUBE_DEAD_VOLUME_UL
            )
            loading_list.append(("reagent", reagent_position, reagent_name, volume))

        loading_list.append(("reagent", MIXING_TUBE_POSITION, "master mix", None))

        return loading_list

    def invoke(self, operation: str) -> Mapping[str, float] | None:

        if operation == "prepare_master_mix":
            total_reactions = master_mix_reactions(len(self.samples))
            try:
                for _, position, volume in MASTER_MIX_RECIPE:
                    self.pipette_1000.transfer(
                        volume=volume * total_reactions,
                        source=self.reagent_rack[position],
                        dest=self.reagent_rack[MIXING_TUBE_POSITION],
                        new_tip="always",
                        mix_after=(
                            MASTER_MIX_RINSING_REPETITIONS,
                            MASTER_MIX_RINSING_VOLUME_UL,
                        ),
                    )
                self.pipette_1000.pick_up_tip()
                self.pipette_1000.mix(
                    MASTER_MIX_FINAL_MIX_REPETITIONS,
                    MASTER_MIX_FINAL_MIX_VOLUME_UL,
                    self.reagent_rack[MIXING_TUBE_POSITION],
                )
                self.pipette_1000.drop_tip()
            except Exception as exc:
                msg = f"{operation} failed: {exc}"
                raise RuntimeError(msg) from exc
            return None

        if operation == "distribute_master_mix":
            try:
                self.pipette_50.configure_for_volume(MASTER_MIX_VOLUME_UL)
                self.pipette_50.transfer(
                    volume=MASTER_MIX_VOLUME_UL,
                    source=self.reagent_rack[MIXING_TUBE_POSITION],
                    dest=[self.plate[well] for well in self.samples],
                    new_tip="once",
                )
            except Exception as exc:
                msg = f"{operation} failed: {exc}"
                raise RuntimeError(msg) from exc
            return None

        if operation == "prepare_standards":
            # A single standard leaves nothing to dilute, and the vendor's transfer
            # raises on an empty destination list.
            if not self.dilution_plan:
                return None
            try:
                self.pipette_50.configure_for_volume(DILUTION_MIXING_VOLUME_UL)
                self.pipette_50.transfer(
                    volume=[
                        water_volume_ul
                        for _, _, water_volume_ul in self.dilution_plan.values()
                    ],
                    source=self.sample_rack[SAMPLE_NUCLEASE_FREE_WATER_TUBE_POSITION],
                    dest=[
                        self.sample_tubes[receiving] for receiving in self.dilution_plan
                    ],
                    new_tip="once",
                )
                for receiving, (
                    source,
                    transfer_volume_ul,
                    _,
                ) in self.dilution_plan.items():
                    self.pipette_50.transfer(
                        volume=transfer_volume_ul,
                        source=self.sample_tubes[source],
                        dest=self.sample_tubes[receiving],
                        new_tip="always",
                        mix_after=(
                            DILUTION_MIXING_REPETITIONS,
                            DILUTION_MIXING_VOLUME_UL,
                        ),
                    )
            except Exception as exc:
                msg = f"{operation} failed: {exc}"
                raise RuntimeError(msg) from exc
            return None

        if operation == "add_sample":
            try:
                self.pipette_50.configure_for_volume(SAMPLE_VOLUME_UL)
                for well, sample in self.samples.items():
                    self.pipette_50.transfer(
                        volume=SAMPLE_VOLUME_UL,
                        source=self.sample_tubes[sample],
                        dest=self.plate[well],
                        new_tip="always",
                        mix_after=(SAMPLE_MIXING_REPETITIONS, SAMPLE_MIXING_VOLUME_UL),
                    )
            except Exception as exc:
                msg = f"{operation} failed: {exc}"
                raise RuntimeError(msg) from exc
            return None

        msg = f"unknown operation: {operation!r}"
        raise ValueError(msg)
