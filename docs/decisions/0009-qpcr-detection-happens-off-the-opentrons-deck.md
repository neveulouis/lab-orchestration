# 0009, qPCR detection happens off the Opentrons deck

## Status

Accepted, 2026-10-27.

## Context

The run prepares a qPCR plate on the liquid handler, then reads fluorescence
every cycle. Opentrons does not make any qPCR fluorescence reader. In a real lab
the plate would leave the Flex for a qPCR instrument from another vendor.

Three alternatives were rejected: running the program on the Opentrons
Thermocycler Module (it reads no fluorescence, and it would run the program
instead of the engine), loading the plate in the Opentrons Thermocycler Module
and acquiring with this project's `Thermocycler` (two thermocyclers, one
reading), or moving the plate to a deck slot standing for this project's
`Thermocycler` (implies an on-deck detector that does not exist).

## Decision

The engine's `Thermocycler` stands for the external qPCR instrument. It is
outside the Opentrons context and imports nothing from `opentrons`. The liquid
handler's last step moves the plate to `OFF_DECK` with `use_gripper=False`: the
operator's handoff, dispatched by name like any step.

## Consequences

- Cost: the move is manual. On a real Flex, the run pauses until an operator
  confirms it.
- The `Thermocycler` does not check that a plate arrived: checking would mean
  reading the Opentrons context.
- No engine or interface change.
- No document may imply that Opentrons performs detection.
