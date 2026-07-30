"""qPCR workflow definition."""

from lab_orchestration.engine import Program, Repeat, Step

QPCR_PROGRAM: Program = [
    Step("initial_denaturation", 300),
    Repeat(
        40, [Step("denaturation", 15), Step("annealing", 30), Step("extension", 30)]
    ),
]
