import random
from db.repositories.drawings import DrawingsRepository
from services.generate_numbers import generate_number_with_range, compute_weighted_frequencies
from services.fetch_numbers import check_numbers, save_generation
from constants import GENERATIVE_RANDOMNESS_RANGE, NUMBER_GENERATION_RANGE, ALT_CHANGE_RANGE


def generate_powerball_drawing_v1(drawing_count):
    numbers = []
    drawn_powerball_numbers = set()
    existing_drawing = False
    for _ in range(drawing_count):
        first_alt = random.random() >= 0.81
        last_alt = random.random() >= 0.80

        if first_alt:
            first_number = random.randint(NUMBER_GENERATION_RANGE["first_number_alt"][0], NUMBER_GENERATION_RANGE["first_number_alt"][1])
            second_number = random.randint(max(first_number + 1, NUMBER_GENERATION_RANGE["second_number_alt"][0]), NUMBER_GENERATION_RANGE["second_number_alt"][1])
            third_number = random.randint(max(second_number + 1, NUMBER_GENERATION_RANGE["third_number_alt"][0]), NUMBER_GENERATION_RANGE["third_number_alt"][1])
        else:
            first_number = random.randint(NUMBER_GENERATION_RANGE["first_number"][0], NUMBER_GENERATION_RANGE["first_number"][1])
            second_number = random.randint(max(first_number + 1, NUMBER_GENERATION_RANGE["second_number"][0]), NUMBER_GENERATION_RANGE["second_number"][1])
            third_number = random.randint(max(second_number + 1, NUMBER_GENERATION_RANGE["third_number"][0]), NUMBER_GENERATION_RANGE["third_number"][1])

        if last_alt:
            fifth_number = random.randint(max(third_number + 1, NUMBER_GENERATION_RANGE["fifth_number_alt"][0]), NUMBER_GENERATION_RANGE["fifth_number_alt"][1])
            fourth_number = random.randint(third_number + 1, fifth_number - 1)
        else:
            fourth_number = random.randint(max(third_number + 1, NUMBER_GENERATION_RANGE["fourth_number"][0]), NUMBER_GENERATION_RANGE["fourth_number"][1])
            fifth_number = random.randint(max(fourth_number + 1, NUMBER_GENERATION_RANGE["fifth_number"][0]), NUMBER_GENERATION_RANGE["fifth_number"][1])

        powerball_number = random.randint(1, 26)
        while powerball_number in drawn_powerball_numbers:
            powerball_number = random.randint(1, 26)
        drawn_powerball_numbers.add(powerball_number)

        numbers.append([
            {"first_number": first_number},
            {"second_number": second_number},
            {"third_number": third_number},
            {"fourth_number": fourth_number},
            {"fifth_number": fifth_number},
            {"powerball_number": powerball_number}
        ])
        numbers_exists = check_numbers(first_number, second_number, third_number, fourth_number, fifth_number)
        if numbers_exists:
            existing_drawing = True

    return {
        "numbers": numbers,
        "drawn_before": True if existing_drawing else False,
    }


def generate_powerball_drawing_v2(drawing_count, should_save_generation):
    numbers = []
    existing_drawing = False
    for _ in range(drawing_count):
        first_alt = random.random()

        if first_alt <= ALT_CHANGE_RANGE["first_number"][0]:
            first_number = random.randint(NUMBER_GENERATION_RANGE["first_number"][0], NUMBER_GENERATION_RANGE["first_number"][1])
        elif first_alt > ALT_CHANGE_RANGE["first_number"][0] and first_alt <= ALT_CHANGE_RANGE["first_number"][1]:
            first_number = random.randint(NUMBER_GENERATION_RANGE["first_number_alt"][0], NUMBER_GENERATION_RANGE["first_number_alt"][1])
        elif first_alt > ALT_CHANGE_RANGE["first_number"][1]:
            first_number = random.randint(NUMBER_GENERATION_RANGE["first_number_alt_alt"][0], NUMBER_GENERATION_RANGE["first_number_alt_alt"][1])
        else:
            first_number = random.randint(NUMBER_GENERATION_RANGE["first_number"][0], NUMBER_GENERATION_RANGE["first_number_alt"][1])

        fifth_alt = random.random()
        fifth_number = None

        while fifth_number is None:
            if fifth_alt <= ALT_CHANGE_RANGE["fifth_number"][0]:
                fifth_number = random.randint(NUMBER_GENERATION_RANGE["fifth_number"][0], NUMBER_GENERATION_RANGE["fifth_number"][1])
            elif fifth_alt > ALT_CHANGE_RANGE["fifth_number"][0] and fifth_alt <= ALT_CHANGE_RANGE["fifth_number"][1]:
                fifth_number = random.randint(NUMBER_GENERATION_RANGE["fifth_number_alt"][0], NUMBER_GENERATION_RANGE["fifth_number_alt"][1])
            elif fifth_alt > ALT_CHANGE_RANGE["fifth_number"][1]:
                fifth_number = random.randint(NUMBER_GENERATION_RANGE["fifth_number_alt_alt"][0], NUMBER_GENERATION_RANGE["fifth_number_alt_alt"][1])
                while fifth_number - first_number <= 10:
                    fifth_number = random.randint(NUMBER_GENERATION_RANGE["fifth_number_alt_alt"][0], NUMBER_GENERATION_RANGE["fifth_number_alt_alt"][1])
            else:
                fifth_number = random.randint(NUMBER_GENERATION_RANGE["fifth_number_alt"][0], NUMBER_GENERATION_RANGE["fifth_number"][1])

            if fifth_number <= first_number + 12:
                fifth_number = None

        second_number = None
        while second_number is None:
            second_alt = random.random()

            if second_alt <= ALT_CHANGE_RANGE["second_number"][0]:
                second_number = random.randint(NUMBER_GENERATION_RANGE["second_number"][0], NUMBER_GENERATION_RANGE["second_number"][1])
            elif second_alt > ALT_CHANGE_RANGE["second_number"][0] and second_alt <= ALT_CHANGE_RANGE["second_number"][1]:
                second_number = random.randint(NUMBER_GENERATION_RANGE["second_number_alt"][0], NUMBER_GENERATION_RANGE["second_number_alt"][1])
            elif second_alt > ALT_CHANGE_RANGE["second_number"][1]:
                second_number = random.randint(NUMBER_GENERATION_RANGE["second_number_alt_alt"][0], NUMBER_GENERATION_RANGE["second_number_alt_alt"][1])
            else:
                second_number = random.randint(NUMBER_GENERATION_RANGE["second_number_alt"][0], NUMBER_GENERATION_RANGE["second_number"][1])

            if second_number <= first_number or second_number >= fifth_number:
                second_number = None

        fourth_number = None
        while fourth_number is None:
            fourth_alt = random.random()

            if fourth_alt <= ALT_CHANGE_RANGE["fourth_number"][0]:
                fourth_number = random.randint(NUMBER_GENERATION_RANGE["fourth_number"][0], NUMBER_GENERATION_RANGE["fourth_number"][1])
            elif fourth_alt > ALT_CHANGE_RANGE["fourth_number"][0] and fourth_alt <= ALT_CHANGE_RANGE["fourth_number"][1]:
                fourth_number = random.randint(NUMBER_GENERATION_RANGE["fourth_number_alt"][0], NUMBER_GENERATION_RANGE["fourth_number_alt"][1])
            elif fourth_alt > ALT_CHANGE_RANGE["fourth_number"][1]:
                fourth_number = random.randint(NUMBER_GENERATION_RANGE["fourth_number_alt_alt"][0], NUMBER_GENERATION_RANGE["fourth_number_alt_alt"][1])
            else:
                fourth_number = random.randint(NUMBER_GENERATION_RANGE["fourth_number_alt"][0], NUMBER_GENERATION_RANGE["fourth_number"][1])

            if fourth_number >= fifth_number or fourth_number <= second_number or fourth_number - second_number == 1:
                fourth_number = None

        third_number = None
        while third_number is None:
            third_alt = random.random()

            if third_alt <= ALT_CHANGE_RANGE["third_number"][0]:
                third_number = random.randint(NUMBER_GENERATION_RANGE["third_number"][0], NUMBER_GENERATION_RANGE["third_number"][1])
            elif third_alt > ALT_CHANGE_RANGE["third_number"][0] and third_alt <= ALT_CHANGE_RANGE["third_number"][1]:
                third_number = random.randint(NUMBER_GENERATION_RANGE["third_number_alt"][0], NUMBER_GENERATION_RANGE["third_number_alt"][1])
            elif third_alt > ALT_CHANGE_RANGE["third_number"][1]:
                third_number = random.randint(NUMBER_GENERATION_RANGE["third_number_alt_alt"][0], NUMBER_GENERATION_RANGE["third_number_alt_alt"][1])
            else:
                third_number = random.randint(NUMBER_GENERATION_RANGE["third_number_alt"][0], NUMBER_GENERATION_RANGE["third_number"][1])

            if third_number <= second_number or third_number >= fourth_number:
                third_number = None

        powerball_number = random.randint(1, 26)

        numbers.append([
            {"first_number": first_number},
            {"second_number": second_number},
            {"third_number": third_number},
            {"fourth_number": fourth_number},
            {"fifth_number": fifth_number},
            {"powerball_number": powerball_number}
        ])
        numbers_exists = check_numbers(first_number, second_number, third_number, fourth_number, fifth_number)
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


def generate_powerball_drawing_v3(drawing_count, should_save_generation, range_date):
    numbers = []
    existing_drawing = False
    first_number_ranges = list(DrawingsRepository.fetch_occurance_by_ball_position("first_ball", range_date))
    second_number_ranges = list(DrawingsRepository.fetch_occurance_by_ball_position("second_ball", range_date))
    third_number_ranges = list(DrawingsRepository.fetch_occurance_by_ball_position("third_ball", range_date))
    fourth_number_ranges = list(DrawingsRepository.fetch_occurance_by_ball_position("fourth_ball", range_date))
    fifth_number_ranges = list(DrawingsRepository.fetch_occurance_by_ball_position("fifth_ball", range_date))
    power_ball_number_ranges = list(DrawingsRepository.fetch_occurance_by_ball_position("power_ball", range_date))
    for i, _ in enumerate(range(drawing_count)):
        if i % 2 == 0:
            for _ in range(0, 10):
                first_number = generate_number_with_range(first_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_with_range(second_number_ranges)
                while second_number <= first_number:
                    second_number = generate_number_with_range(second_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_with_range(third_number_ranges)
                while third_number <= second_number:
                    third_number = generate_number_with_range(third_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_with_range(fourth_number_ranges)
                while fourth_number <= third_number:
                    fourth_number = generate_number_with_range(fourth_number_ranges)

            for _ in range(0, 10):
                fifth_number = generate_number_with_range(fifth_number_ranges)
                while fifth_number <= fourth_number:
                    fifth_number = generate_number_with_range(fifth_number_ranges)
        else:
            for _ in range(0, 10):
                fifth_number = generate_number_with_range(fifth_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_with_range(fourth_number_ranges)
                while fourth_number >= fifth_number:
                    fourth_number = generate_number_with_range(fourth_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_with_range(third_number_ranges)
                while third_number >= fourth_number:
                    third_number = generate_number_with_range(third_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_with_range(second_number_ranges)
                while second_number >= third_number:
                    second_number = generate_number_with_range(second_number_ranges)

            for _ in range(0, 10):
                first_number = generate_number_with_range(first_number_ranges)
                while first_number >= second_number:
                    first_number = generate_number_with_range(first_number_ranges)

        for _ in range(0, 10):
            power_ball = generate_number_with_range(power_ball_number_ranges)

        numbers.append([
            {"first_number": first_number},
            {"second_number": second_number},
            {"third_number": third_number},
            {"fourth_number": fourth_number},
            {"fifth_number": fifth_number},
            {"powerball_number": power_ball}
        ])

        numbers_exists = check_numbers(first_number, second_number, third_number, fourth_number, fifth_number)
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


def generate_powerball_drawing_v4(drawing_count, should_save_generation, range_date):
    numbers = []
    existing_drawing = False
    number_ranges = list(DrawingsRepository.fetch_occurance_by_number(range_date))
    total_percent = sum(r[2] for r in number_ranges)
    normalized_ranges = [(num, count, pct / total_percent) for num, count, pct in number_ranges]

    power_ball_number_ranges = list(DrawingsRepository.fetch_occurance_by_ball_position("power_ball", range_date))
    for _ in range(drawing_count):
        generation = []
        for _ in range(5):
            gen_num = None

            while gen_num is None or gen_num in generation:
                rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
                for _ in range(rand):
                    gen_num = generate_number_with_range(normalized_ranges)

            generation.append(gen_num)

        rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
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


def generate_powerball_drawing_v5(drawing_count, should_save_generation):
    numbers = []
    existing_drawing = False
    numbers_with_date = list(DrawingsRepository.fetch_occurance_with_num_and_date())
    number_ranges = compute_weighted_frequencies(numbers_with_date)
    total_percent = sum(r[2] for r in number_ranges)
    normalized_ranges = [(num, count, pct / total_percent) for num, count, pct in number_ranges]

    power_ball_numbers_with_date = list(DrawingsRepository.fetch_power_ball_occurance_with_num_and_date())
    power_ball_number_ranges = compute_weighted_frequencies(power_ball_numbers_with_date)
    for _ in range(drawing_count):
        generation = []
        for _ in range(5):
            gen_num = None

            while gen_num is None or gen_num in generation:
                rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
                for _ in range(rand):
                    gen_num = generate_number_with_range(normalized_ranges)

            generation.append(gen_num)

        rand = random.randint(1, GENERATIVE_RANDOMNESS_RANGE)
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
