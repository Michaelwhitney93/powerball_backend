import random
from db.repositories.drawings import DrawingsRepository
from services.algorithms import (
    build_registry,
    sum_range_builder,
    odd_even_builder,
    make_constrained,
)

VALID_CONSTRAINTS = {"sum_range", "odd_even"}


def _build_lookup(registry: list) -> dict:
    lookup = {}
    for algo in registry:
        key = algo.__name__.removesuffix("_constrained")
        if key.startswith("state_conditioned"):
            key = "state_conditioned"
        lookup[key] = algo
    return lookup


def generate_multi(count: int, constraints: list[str], algorithm: str = "random"):
    drawings = DrawingsRepository.get_all_drawings()
    registry = build_registry(drawings)

    constraint_factories = []
    if "sum_range" in constraints:
        constraint_factories.append(sum_range_builder(drawings))
    if "odd_even" in constraints:
        constraint_factories.append(odd_even_builder(drawings))

    if constraint_factories:
        registry = [make_constrained(algo, constraint_factories) for algo in registry]

    lookup = _build_lookup(registry)

    if algorithm != "random" and algorithm not in lookup:
        return {
            "error": f"Unknown algorithm '{algorithm}'.",
            "valid_algorithms": sorted(lookup.keys()) + ["random"],
        }, 400

    results = []
    for _ in range(count):
        chosen = random.choice(registry) if algorithm == "random" else lookup[algorithm]
        white, pb = chosen()
        results.append({
            "algorithm": chosen.__name__,
            "white_balls": white,
            "power_ball": pb,
        })

    return {
        "generations": results,
        "count": count,
        "algorithm": algorithm,
        "constraints_applied": [c for c in constraints if c in VALID_CONSTRAINTS],
    }
