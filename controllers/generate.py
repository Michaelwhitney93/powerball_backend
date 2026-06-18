import random
from db.repositories.drawings import DrawingsRepository
from services.generate_numbers import generate_number_with_range, compute_weighted_frequencies
from services.fetch_numbers import check_numbers, save_generation
from constants import WHITE_BALL_RANDOMNESS_RANGE, POWER_BALL_RANDOMNESS_RANGE


def generate_powerball_drawing_v6(drawing_count, should_save_generation):
    numbers = []
    existing_drawing = False
    first_ball_numbers_with_dates = list(DrawingsRepository.fetch_occurance_by_position_and_date("first_ball"))
    second_ball_numbers_with_dates = list(DrawingsRepository.fetch_occurance_by_position_and_date("second_ball"))
    third_ball_numbers_with_dates = list(DrawingsRepository.fetch_occurance_by_position_and_date("third_ball"))
    fourth_ball_numbers_with_dates = list(DrawingsRepository.fetch_occurance_by_position_and_date("fourth_ball"))
    fifth_ball_numbers_with_dates = list(DrawingsRepository.fetch_occurance_by_position_and_date("fifth_ball"))
    first_ball_number_ranges = compute_weighted_frequencies(first_ball_numbers_with_dates)
    second_ball_number_ranges = compute_weighted_frequencies(second_ball_numbers_with_dates)
    third_ball_number_ranges = compute_weighted_frequencies(third_ball_numbers_with_dates)
    fourth_ball_number_ranges = compute_weighted_frequencies(fourth_ball_numbers_with_dates)
    fifth_ball_number_ranges = compute_weighted_frequencies(fifth_ball_numbers_with_dates)

    power_ball_numbers_with_dates = list(DrawingsRepository.fetch_occurance_by_position_and_date("power_ball"))
    power_ball_number_ranges = compute_weighted_frequencies(power_ball_numbers_with_dates)

    for _ in range(drawing_count):
        generation = []
        for idx in range(5):
            rand = random.randint(1, WHITE_BALL_RANDOMNESS_RANGE)
            gen_num = None

            if idx == 0:
                number_ranges = first_ball_number_ranges
            elif idx == 1:
                number_ranges = second_ball_number_ranges
            elif idx == 2:
                number_ranges = third_ball_number_ranges
            elif idx == 3:
                number_ranges = fourth_ball_number_ranges
            elif idx == 4:
                number_ranges = fifth_ball_number_ranges

            while gen_num is None or gen_num in generation:
                for _ in range(rand):
                    gen_num = generate_number_with_range(number_ranges)

            generation.append(gen_num)

        rand = random.randint(1, POWER_BALL_RANDOMNESS_RANGE)
        for _ in range(rand):
            power_ball = generate_number_with_range(power_ball_number_ranges)
        generation.sort()
        generation.append(power_ball)

        numbers.append([
            {"first_number": generation[0]},
            {"second_number": generation[1]},
            {"third_number": generation[2]},
            {"fourth_number": generation[3]},
            {"fifth_number": generation[4]},
            {"powerball_number": generation[5]}
        ])

        numbers_exists = check_numbers(generation[0], generation[1], generation[2], generation[3], generation[4])
        if numbers_exists:
            existing_drawing = True

    if should_save_generation:
        for generation in numbers:
            save_generation(
                generation[0]["first_number"],
                generation[1]["second_number"],
                generation[2]["third_number"],
                generation[3]["fourth_number"],
                generation[4]["fifth_number"],
                generation[5]["powerball_number"]
            )

    return {
        "numbers": numbers,
        "drawn_before": True if existing_drawing else False,
    }

