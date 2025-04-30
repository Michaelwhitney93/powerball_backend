import random
from db.repositories.drawings import fetch_occurance_by_ball_position

def generate_number_by_column(column):
    number_generations_ranges = list(fetch_occurance_by_ball_position(column))
    first_number_range = random.random()
    low_point = 0.0
    high_point = 0.0
    for query_result in number_generations_ranges:
        occurance_percentage = query_result[1]
        number = query_result[2]
        low_point = high_point
        high_point += occurance_percentage
        if first_number_range >= low_point and first_number_range <= high_point:
            return number