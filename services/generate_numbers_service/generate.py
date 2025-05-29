import random


def generate_number_with_range(ranges):
    random_number_point = random.random()
    low_point = 0.0
    high_point = 0.0
    for query_result in ranges:
        occurance_percentage = query_result[2]
        number = query_result[0]
        low_point = high_point
        high_point += occurance_percentage
        if random_number_point >= low_point and random_number_point <= high_point:
            return number
