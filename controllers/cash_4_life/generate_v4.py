import random
from db.repositories.cash_4_life_drawings import Cash4LifeRepository
from services.generate_numbers_service.generate import generate_number_with_range, compute_weighted_frequencies
from services.fetch_numbers_service.cash_4_life.fetch_numbers import check_numbers
from controllers.constants import GENERATIVE_RANDOMNESS_RANGE


def generate_cash_4_life_drawing_v4(drawing_count, range_date):
    numbers = []
    existing_drawing = False
    number_ranges = list(Cash4LifeRepository.fetch_occurance_by_number(range_date))

    cash_ball_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("cash_ball", range_date))
    for _ in range(drawing_count):
        generation = []
        for _ in range(5):
            rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
            gen_num = None

            while gen_num is None or gen_num in generation:
                for _ in range(rand):
                    gen_num = generate_number_with_range(number_ranges)

            generation.append(gen_num)
        
        rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
        for _ in range(rand):
            cash_ball = generate_number_with_range(cash_ball_number_ranges)
        generation.sort()
        generation.append(cash_ball)

        numbers.append([
                {"first_number": generation[0]},
                {"second_number": generation[1]},
                {"third_number": generation[2]},
                {"fourth_number": generation[3]},
                {"fifth_number": generation[4]},
                {"cashball_number": generation[5]}
            ])

        numbers_exists = check_numbers(generation[0], generation[1], generation[2], generation[3], generation[4])
        if numbers_exists:
            existing_drawing = True

    return {
        "numbers": numbers,
        "drawn_before": True if existing_drawing else False,
    }


def generate_cash_4_life_drawing_v5(drawing_count):
    numbers = []
    existing_drawing = False
    numbers_with_dates = list(Cash4LifeRepository.fetch_occurance_with_num_and_date())
    number_ranges = compute_weighted_frequencies(numbers_with_dates)

    cash_ball_numbers_with_dates = list(Cash4LifeRepository.fetch_cash_ball_occurance_with_num_and_date())
    cash_ball_number_ranges = compute_weighted_frequencies(cash_ball_numbers_with_dates)
    for _ in range(drawing_count):
        generation = []
        for _ in range(5):
            rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
            gen_num = None

            while gen_num is None or gen_num in generation:
                for _ in range(rand):
                    gen_num = generate_number_with_range(number_ranges)

            generation.append(gen_num)
        
        rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
        for _ in range(rand):
            cash_ball = generate_number_with_range(cash_ball_number_ranges)
        generation.sort()
        generation.append(cash_ball)

        numbers.append([
                {"first_number": generation[0]},
                {"second_number": generation[1]},
                {"third_number": generation[2]},
                {"fourth_number": generation[3]},
                {"fifth_number": generation[4]},
                {"cashball_number": generation[5]}
            ])

        numbers_exists = check_numbers(generation[0], generation[1], generation[2], generation[3], generation[4])
        if numbers_exists:
            existing_drawing = True

    return {
        "numbers": numbers,
        "drawn_before": True if existing_drawing else False,
    }


def generate_cash_4_life_drawing_overtime_v4(drawing_count):
    numbers = []
    existing_drawing = False
    all_time_date = '2014-06-16'
    five_year_date = '2020-05-27'
    two_year_date = '2023-05-27'
    one_year_date = '2024-05-27'
    six_months_date = '2024-12-27'

    for idx, _ in enumerate(range(5)):
        if idx == 0:
            range_date = all_time_date
        elif idx == 1:
            range_date = five_year_date
        elif idx == 2:
            range_date = two_year_date
        elif idx == 3:
            range_date = one_year_date
        elif idx == 4:
            range_date = six_months_date

        number_ranges = list(Cash4LifeRepository.fetch_occurance_by_number(range_date))

        cash_ball_number_ranges = list(Cash4LifeRepository.fetch_occurance_by_ball_position("cash_ball", range_date))
        for _ in range(drawing_count):
            generation = []
            for _ in range(5):
                rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
                gen_num = None

                while gen_num is None or gen_num in generation:
                    for _ in range(rand):
                        gen_num = generate_number_with_range(number_ranges)

                generation.append(gen_num)
            
            rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
            for _ in range(rand):
                cash_ball = generate_number_with_range(cash_ball_number_ranges)
            generation.sort()
            generation.append(cash_ball)

            numbers.append([
                    {"first_number": generation[0]},
                    {"second_number": generation[1]},
                    {"third_number": generation[2]},
                    {"fourth_number": generation[3]},
                    {"fifth_number": generation[4]},
                    {"cashball_number": generation[5]}
                ])

            numbers_exists = check_numbers(generation[0], generation[1], generation[2], generation[3], generation[4])
            if numbers_exists:
                existing_drawing = True

    return {
        "numbers": numbers,
        "drawn_before": True if existing_drawing else False,
    }