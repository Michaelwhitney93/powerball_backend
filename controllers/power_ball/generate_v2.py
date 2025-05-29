import random
from services.fetch_numbers_service.constants import NUMBER_GENERATION_RANGE, ALT_CHANGE_RANGE
from services.fetch_numbers_service.powerball.fetch_numbers import check_numbers, save_generation


def generate_power_ball_drawing_v2(drawing_count, should_save_generation):
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
# <-------------------------------------------------------------------------------------------------------------------------------------------------->
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
# <-------------------------------------------------------------------------------------------------------------------------------------------------->
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
# <-------------------------------------------------------------------------------------------------------------------------------------------------->
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
# <-------------------------------------------------------------------------------------------------------------------------------------------------->
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
# <-------------------------------------------------------------------------------------------------------------------------------------------------->
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
