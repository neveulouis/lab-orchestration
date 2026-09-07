"""qPCR workflow definition."""

from lab_orchestration.engine import Program, Repeat, Step

QPCR_PROGRAM: Program = [
    Step("liquid_handler", "distribute_master_mix", 20),
    Step("liquid_handler", "add_sample", 30),
    Step("thermocycler", "initial_denaturation", 300),
    Repeat(
        40,
        [
            Step("thermocycler", "denaturation", 15),
            Step("thermocycler", "annealing", 30),
            Step("thermocycler", "extension", 30),
        ],
    ),
]
