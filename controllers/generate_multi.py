import random
from db.repositories.drawings import DrawingsRepository
from services.algorithms import (
    build_registry,
    sum_range_builder,
    odd_even_builder,
    make_constrained,
)

VALID_CONSTRAINTS = {"sum_range", "odd_even"}


def generate_multi(count: int, constraints: list[str]):
    drawings = DrawingsRepository.get_all_drawings()
    registry = build_registry(drawings)

    constraint_factories = []
    if "sum_range" in constraints:
        constraint_factories.append(sum_range_builder(drawings))
    if "odd_even" in constraints:
        constraint_factories.append(odd_even_builder(drawings))

    if constraint_factories:
        registry = [make_constrained(algo, constraint_factories) for algo in registry]

    results = []
    for _ in range(count):
        algo = random.choice(registry)
        white, pb = algo()
        results.append({
            "algorithm": algo.__name__,
            "white_balls": white,
            "power_ball": pb,
        })

    return {
        "generations": results,
        "count": count,
        "constraints_applied": [c for c in constraints if c in VALID_CONSTRAINTS],
    }
