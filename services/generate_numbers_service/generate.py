import random
import math
from datetime import datetime
from collections import defaultdict
from controllers.constants import GENERATIVE_RANDOMNESS_RANGE


def generate_number_with_range(ranges):
    # random_number_point = random.random()
    # low_point = 0.0
    # high_point = 0.0
    # for query_result in ranges:
    #     occurance_percentage = query_result[2]
    #     number = query_result[0]
    #     low_point = high_point
    #     high_point += occurance_percentage
    #     if low_point <= random_number_point < high_point:
    #         return number

    # Generate random point
    for _ in range(random.randint(1, GENERATIVE_RANDOMNESS_RANGE)):
        random_point = random.uniform(0, 1)

    cumulative = 0.0
    for number, count, percent in ranges:
        cumulative += percent
        if random_point < cumulative:
            return number


def decay_weight(days_since_draw, half_life_days=180):
    """Returns a weight based on how many days ago the draw happened."""
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

    # Normalize to percent (optional)
    total_weight = sum(number_weights.values())
    weighted_percents = [
        (number, number_count[number], weight / total_weight) for number, weight in number_weights.items()
    ]

    return weighted_percents