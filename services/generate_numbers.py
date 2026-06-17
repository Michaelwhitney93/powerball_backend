import random
import math
from datetime import datetime
from collections import defaultdict
from constants import GENERATIVE_RANDOMNESS_RANGE


def generate_number_with_range(ranges):
    for _ in range(random.randint(1, GENERATIVE_RANDOMNESS_RANGE)):
        random_point = random.uniform(0, 1)

    cumulative = 0.0
    for number, count, percent in ranges:
        cumulative += percent
        if random_point < cumulative:
            return number


def decay_weight(days_since_draw, half_life_days=180):
    return math.exp(-math.log(2) * days_since_draw / half_life_days)


def compute_weighted_frequencies(results, half_life_days=365):
    now = datetime.now()
    number_weights = defaultdict(float)
    number_count = defaultdict(int)

    for number, draw_date in results:
        days_old = (now - draw_date).days
        weight = decay_weight(days_old, half_life_days)
        number_weights[number] += weight
        number_count[number] += 1

    total_weight = sum(number_weights.values())
    weighted_percents = [
        (number, number_count[number], weight / total_weight) for number, weight in number_weights.items()
    ]

    return weighted_percents
