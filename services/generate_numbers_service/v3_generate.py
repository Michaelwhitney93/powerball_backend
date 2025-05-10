import random
from db.repositories.drawings import fetch_occurance_by_number

def generate_number_by_column(ranges):
    first_number_range = random.random()
    low_point = 0.0
    high_point = 0.0
    for query_result in ranges:
        occurance_percentage = query_result[1]
        number = query_result[2]
        low_point = high_point
        high_point += occurance_percentage
        if first_number_range >= low_point and first_number_range <= high_point:
            return number
        

def get_occurance_by_number(number):
    occurances = fetch_occurance_by_number(number)
    return occurances