from db.repositories.power_ball_drawings import PowerballRepository
from services.generate_numbers_service.generate import generate_number_with_range
from services.fetch_numbers_service.powerball.fetch_numbers import check_numbers, save_generation


def generate_power_ball_drawing_v3(drawing_count, should_save_generation, range_date):
    numbers = []
    existing_drawing = False
    first_number_ranges = list(PowerballRepository.fetch_occurance_by_ball_position("first_ball", range_date))
    second_number_ranges = list(PowerballRepository.fetch_occurance_by_ball_position("second_ball", range_date))
    third_number_ranges = list(PowerballRepository.fetch_occurance_by_ball_position("third_ball", range_date))
    fourth_number_ranges = list(PowerballRepository.fetch_occurance_by_ball_position("fourth_ball", range_date))
    fifth_number_ranges = list(PowerballRepository.fetch_occurance_by_ball_position("fifth_ball", range_date))
    power_ball_number_ranges = list(PowerballRepository.fetch_occurance_by_ball_position("power_ball", range_date))
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

        # for _ in range(0, 10):
        #     first_number = generate_number_by_column(first_number_ranges)

        # for _ in range(0, 10):
        #     fifth_number = generate_number_by_column(fifth_number_ranges)
        #     while fifth_number <= first_number + 12:
        #         fifth_number = generate_number_by_column(fifth_number_ranges)

        # for _ in range(0, 10):
        #     second_number = generate_number_by_column(second_number_ranges)
        #     while second_number <= first_number or second_number + 3 >= fifth_number:
        #         second_number = generate_number_by_column(second_number_ranges)

        # for _ in range(0, 10):
        #     fourth_number = generate_number_by_column(fourth_number_ranges)
        #     while fourth_number <= second_number + 2 or fourth_number >= fifth_number:
        #         fourth_number = generate_number_by_column(fourth_number_ranges)

        # for _ in range(0, 10):
        #     third_number = generate_number_by_column(third_number_ranges)
        #     while third_number <= second_number or third_number >= fourth_number:
        #         third_number = generate_number_by_column(third_number_ranges)

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
