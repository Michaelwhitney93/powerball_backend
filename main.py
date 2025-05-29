import random
import requests
from flask import Flask, request
from db.engine import init_db, tear_down_db
from db.repositories.drawings import fetch_occurance_by_ball_position, fetch_occurance_by_number
from db.repositories.cash_4_life_drawings import fetch_occurance_by_ball_position as cash_4_life_fetch_occurance_by_ball, get_all_drawings, fetch_occurance_by_number as cash_4_life_fetch_occurance_by_num
from db.repositories.generations import get_all
from services.fetch_numbers_service.fetch_numbers import populate_drawings, populate_cash_4_life, check_numbers, save_generation, check_cash_4_life_numbers
from services.fetch_numbers_service.constants import NUMBER_GENERATION_RANGE, ALT_CHANGE_RANGE
from services.generate_numbers_service.v3_generate import generate_number_by_column, get_occurance_by_number

app = Flask(__name__)
init_db()


@app.route("/")
def default():
    return "<p>Hello World!</p>"


@app.route("/drawings/powerball")
def get_drawings():
    try:
        populate_drawings()
        return {}, 204
    except requests.exceptions.RequestException as e:
        return f"Request Failed: {e}", 500


@app.route("/drawings/cash4life")
def populate_cash_4_life_drawings():
    try:
        populate_cash_4_life()
        return {}, 204
    except requests.exceptions.RequestException as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/random/v1")
def generate_random_drawing_v1():
    drawing_count = int(request.args.get("drawings", "1"))
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


@app.route("/generate/random/v2")
def generate_random_drawing_v2():
    drawing_count = int(request.args.get("drawings", "1"))
    should_save_generation = request.args.get("save_generation", "False") == "True"
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


@app.route("/generate/powerball/random/v3")
def generate_random_drawing_v3():
    drawing_count = int(request.args.get("drawings", "1"))
    should_save_generation = request.args.get("save_generation", "False") == "True"
    range_date = request.args.get("start_date", "2015-10-03")
    numbers = []
    existing_drawing = False
    first_number_ranges = list(fetch_occurance_by_ball_position("first_ball", range_date))
    second_number_ranges = list(fetch_occurance_by_ball_position("second_ball", range_date))
    third_number_ranges = list(fetch_occurance_by_ball_position("third_ball", range_date))
    fourth_number_ranges = list(fetch_occurance_by_ball_position("fourth_ball", range_date))
    fifth_number_ranges = list(fetch_occurance_by_ball_position("fifth_ball", range_date))
    power_ball_number_ranges = list(fetch_occurance_by_ball_position("power_ball", range_date))
    for i, _ in enumerate(range(drawing_count)):
        if i % 2 == 0:
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number <= first_number:
                    second_number = generate_number_by_column(second_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number <= second_number:
                    third_number = generate_number_by_column(third_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number <= third_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
                while fifth_number <= fourth_number:
                    fifth_number = generate_number_by_column(fifth_number_ranges)
        else:
            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
            
            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number >= fifth_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number >= fourth_number:
                    third_number = generate_number_by_column(third_number_ranges)
            
            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number >= third_number:
                    second_number = generate_number_by_column(second_number_ranges)
            
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)
                while first_number >= second_number:
                    first_number = generate_number_by_column(first_number_ranges)

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
            power_ball = generate_number_by_column(power_ball_number_ranges)

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


@app.route("/generate/powerball/random/v4")
def generate_random_powerball_drawing_v4():
    drawing_count = int(request.args.get("drawings", "1"))
    should_save_generation = request.args.get("save_generation", "False") == "True"
    range_date = request.args.get("start_date", "2015-10-03")
    numbers = []
    existing_drawing = False
    number_ranges = list(fetch_occurance_by_number(range_date))

    total_count = 0
    for tuple in number_ranges:
        count = tuple[0]
        total_count += count

    print(number_ranges)
    power_ball_number_ranges = list(fetch_occurance_by_ball_position("power_ball", range_date))
    for _ in range(drawing_count):
        generation = []
        for _ in range(5):
            rand = random.randint(1, 10)
            gen_num = None

            while gen_num is None or gen_num in generation:
                for _ in range(rand):
                    gen_num = generate_number_by_column(number_ranges)

            generation.append(gen_num)
        
        rand = random.randint(1, 10)
        for _ in range(rand):
            power_ball = generate_number_by_column(power_ball_number_ranges)
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


@app.route("/generate/powerball/overtime")
def generate_powerball_numbers_over_time():
    drawing_count = int(request.args.get("drawings", "1"))
    numbers = []
    existing_drawing = False
    all_time_date = '2015-10-03'
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

        first_number_ranges = list(fetch_occurance_by_ball_position("first_ball", range_date))
        second_number_ranges = list(fetch_occurance_by_ball_position("second_ball", range_date))
        third_number_ranges = list(fetch_occurance_by_ball_position("third_ball", range_date))
        fourth_number_ranges = list(fetch_occurance_by_ball_position("fourth_ball", range_date))
        fifth_number_ranges = list(fetch_occurance_by_ball_position("fifth_ball", range_date))
        power_ball_number_ranges = list(fetch_occurance_by_ball_position("power_ball", range_date))
        for i, _ in enumerate(range(drawing_count)):
            if i % 2 == 0:
                for _ in range(0, 10):
                    first_number = generate_number_by_column(first_number_ranges)

                for _ in range(0, 10):
                    second_number = generate_number_by_column(second_number_ranges)
                    while second_number <= first_number:
                        second_number = generate_number_by_column(second_number_ranges)

                for _ in range(0, 10):
                    third_number = generate_number_by_column(third_number_ranges)
                    while third_number <= second_number:
                        third_number = generate_number_by_column(third_number_ranges)

                for _ in range(0, 10):
                    fourth_number = generate_number_by_column(fourth_number_ranges)
                    while fourth_number <= third_number:
                        fourth_number = generate_number_by_column(fourth_number_ranges)

                for _ in range(0, 10):
                    fifth_number = generate_number_by_column(fifth_number_ranges)
                    while fifth_number <= fourth_number:
                        fifth_number = generate_number_by_column(fifth_number_ranges)
            else:
                for _ in range(0, 10):
                    fifth_number = generate_number_by_column(fifth_number_ranges)
                
                for _ in range(0, 10):
                    fourth_number = generate_number_by_column(fourth_number_ranges)
                    while fourth_number >= fifth_number:
                        fourth_number = generate_number_by_column(fourth_number_ranges)

                for _ in range(0, 10):
                    third_number = generate_number_by_column(third_number_ranges)
                    while third_number >= fourth_number:
                        third_number = generate_number_by_column(third_number_ranges)
                
                for _ in range(0, 10):
                    second_number = generate_number_by_column(second_number_ranges)
                    while second_number >= third_number:
                        second_number = generate_number_by_column(second_number_ranges)
                
                for _ in range(0, 10):
                    first_number = generate_number_by_column(first_number_ranges)
                    while first_number >= second_number:
                        first_number = generate_number_by_column(first_number_ranges)

            for _ in range(0, 10):
                power_ball = generate_number_by_column(power_ball_number_ranges)

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

    return {
        "numbers": numbers,
        "drawn_before": True if existing_drawing else False,
    }


@app.route("/generate/cash4life/overtime")
def generate_cash_4_life_numbers_over_time():
    drawing_count = int(request.args.get("drawings", "1"))
    numbers = []
    existing_drawing = False
    all_time_date = '2014-06-16'
    five_year_date = '2020-05-27'
    two_year_date = '2023-05-27'
    one_year_date = '2024-05-27'
    six_months_date = '2024-12-27'

    for idx, _ in enumerate(range(drawing_count)):
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

        first_number_ranges = list(cash_4_life_fetch_occurance_by_ball("first_ball", range_date))
        second_number_ranges = list(cash_4_life_fetch_occurance_by_ball("second_ball", range_date))
        third_number_ranges = list(cash_4_life_fetch_occurance_by_ball("third_ball", range_date))
        fourth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fourth_ball", range_date))
        fifth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fifth_ball", range_date))
        cashball_number_ranges = list(cash_4_life_fetch_occurance_by_ball("cash_ball", range_date))
        for i, _ in enumerate(range(5)):
            if i % 2 == 0:
                for _ in range(0, 10):
                    first_number = generate_number_by_column(first_number_ranges)

                for _ in range(0, 10):
                    second_number = generate_number_by_column(second_number_ranges)
                    while second_number <= first_number:
                        second_number = generate_number_by_column(second_number_ranges)

                for _ in range(0, 10):
                    third_number = generate_number_by_column(third_number_ranges)
                    while third_number <= second_number:
                        third_number = generate_number_by_column(third_number_ranges)

                for _ in range(0, 10):
                    fourth_number = generate_number_by_column(fourth_number_ranges)
                    while fourth_number <= third_number:
                        fourth_number = generate_number_by_column(fourth_number_ranges)

                for _ in range(0, 10):
                    fifth_number = generate_number_by_column(fifth_number_ranges)
                    while fifth_number <= fourth_number:
                        fifth_number = generate_number_by_column(fifth_number_ranges)
            else:
                for _ in range(0, 10):
                    fifth_number = generate_number_by_column(fifth_number_ranges)
                
                for _ in range(0, 10):
                    fourth_number = generate_number_by_column(fourth_number_ranges)
                    while fourth_number >= fifth_number:
                        fourth_number = generate_number_by_column(fourth_number_ranges)

                for _ in range(0, 10):
                    third_number = generate_number_by_column(third_number_ranges)
                    while third_number >= fourth_number:
                        third_number = generate_number_by_column(third_number_ranges)
                
                for _ in range(0, 10):
                    second_number = generate_number_by_column(second_number_ranges)
                    while second_number >= third_number:
                        second_number = generate_number_by_column(second_number_ranges)
                
                for _ in range(0, 10):
                    first_number = generate_number_by_column(first_number_ranges)
                    while first_number >= second_number:
                        first_number = generate_number_by_column(first_number_ranges)

            for _ in range(0, 10):
                cash_ball = generate_number_by_column(cashball_number_ranges)

            numbers.append([
                    {"first_number": first_number},
                    {"second_number": second_number},
                    {"third_number": third_number},
                    {"fourth_number": fourth_number},
                    {"fifth_number": fifth_number},
                    {"cashbball_number": cash_ball}
                ])

        numbers_exists = check_numbers(first_number, second_number, third_number, fourth_number, fifth_number)
        if numbers_exists:
            existing_drawing = True

    return {
        "numbers": numbers,
        "drawn_before": True if existing_drawing else False,
    }


@app.route("/generate/cash_4_life/random/v1")
def generate_random_cash4life_drawing_v1():
    drawing_count = int(request.args.get("drawings", "1"))
    range_date = request.args.get("start_date", "2014-06-16")
    numbers = []
    existing_drawing = False
    first_number_ranges = list(cash_4_life_fetch_occurance_by_ball("first_ball", range_date))
    second_number_ranges = list(cash_4_life_fetch_occurance_by_ball("second_ball", range_date))
    third_number_ranges = list(cash_4_life_fetch_occurance_by_ball("third_ball", range_date))
    fourth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fourth_ball", range_date))
    fifth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fifth_ball", range_date))
    cash_ball_number_ranges = list(cash_4_life_fetch_occurance_by_ball("cash_ball", range_date))
    for i, _ in enumerate(range(drawing_count)):
        if i % 2 == 0:
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number <= first_number:
                    second_number = generate_number_by_column(second_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number <= second_number:
                    third_number = generate_number_by_column(third_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number <= third_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
                while fifth_number <= fourth_number:
                    fifth_number = generate_number_by_column(fifth_number_ranges)
        else:
            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
            
            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number >= fifth_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number >= fourth_number:
                    third_number = generate_number_by_column(third_number_ranges)
            
            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number >= third_number:
                    second_number = generate_number_by_column(second_number_ranges)
            
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)
                while first_number >= second_number:
                    first_number = generate_number_by_column(first_number_ranges)
 
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
            cash_ball = generate_number_by_column(cash_ball_number_ranges)

        numbers.append([
                {"first_number": first_number},
                {"second_number": second_number},
                {"third_number": third_number},
                {"fourth_number": fourth_number},
                {"fifth_number": fifth_number},
                {"cashball_number": cash_ball}
            ])

        numbers_exists = check_cash_4_life_numbers(first_number, second_number, third_number, fourth_number, fifth_number)
        if numbers_exists:
            existing_drawing = True

    return {
        "numbers": numbers,
        "drawn_before": True if existing_drawing else False,
    }


@app.route("/test/generations")
def test_generations():
    all_generations = list(get_all())
    successful_generations = []
    for gen in all_generations:
        numbers_exists = check_numbers(
            gen.first_ball, gen.second_ball, gen.third_ball, gen.fourth_ball, gen.fifth_ball, gen.power_ball
        )
        if numbers_exists:
            successful_generations.append(gen)
    
    return successful_generations


@app.route("/test/drawings")
def test_drawings():
    range_date = request.args.get("start_date", "2014-06-16")
    first_number_ranges = list(cash_4_life_fetch_occurance_by_ball("first_ball", range_date))
    second_number_ranges = list(cash_4_life_fetch_occurance_by_ball("second_ball", range_date))
    third_number_ranges = list(cash_4_life_fetch_occurance_by_ball("third_ball", range_date))
    fourth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fourth_ball", range_date))
    fifth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fifth_ball", range_date))
    cash_ball_number_ranges = list(cash_4_life_fetch_occurance_by_ball("cash_ball", range_date))
    v3_generations = []
    v3_number_counts = {}
    for i, _ in enumerate(range(0, 2676)):
        if i % 2 == 0:
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number <= first_number:
                    second_number = generate_number_by_column(second_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number <= second_number:
                    third_number = generate_number_by_column(third_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number <= third_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
                while fifth_number <= fourth_number:
                    fifth_number = generate_number_by_column(fifth_number_ranges)
        else:
            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
            
            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number >= fifth_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number >= fourth_number:
                    third_number = generate_number_by_column(third_number_ranges)
            
            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number >= third_number:
                    second_number = generate_number_by_column(second_number_ranges)
            
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)
                while first_number >= second_number:
                    first_number = generate_number_by_column(first_number_ranges)

        for _ in range(0, 10):
            cash_ball = generate_number_by_column(cash_ball_number_ranges)

        v3_generations.append([
            first_number, second_number, third_number, fourth_number, fifth_number, cash_ball
        ])

    for gen in v3_generations:
        for num in range(1, 60):
            if num == gen[0] or num == gen[1] or num == gen[2] or num == gen[3] or num == gen[4]:
                if v3_number_counts.get(str(num)):
                    v3_number_counts[str(num)]["count"] += 1
                    v3_number_counts[str(num)]["percentage"] = v3_number_counts[str(num)]["count"] / 2676
                else:
                    v3_number_counts[str(num)] = { "num": num, "count": 1, "percentage": 1 / 2676 }

    return {
         "v3_generations": v3_number_counts
    }


@app.route("/test/cashball/generations")
def test_powerball_generations():
    range_date = request.args.get("start_date", "2014-06-16")
    first_number_ranges = list(cash_4_life_fetch_occurance_by_ball("first_ball", range_date))
    second_number_ranges = list(cash_4_life_fetch_occurance_by_ball("second_ball", range_date))
    third_number_ranges = list(cash_4_life_fetch_occurance_by_ball("third_ball", range_date))
    fourth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fourth_ball", range_date))
    fifth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fifth_ball", range_date))
    cash_ball_number_ranges = list(cash_4_life_fetch_occurance_by_ball("cash_ball", range_date))
    for i, _ in enumerate(range(200_000)):
        if i % 2 == 0:
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number <= first_number:
                    second_number = generate_number_by_column(second_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number <= second_number:
                    third_number = generate_number_by_column(third_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number <= third_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
                while fifth_number <= fourth_number:
                    fifth_number = generate_number_by_column(fifth_number_ranges)
        else:
            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
            
            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number >= fifth_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number >= fourth_number:
                    third_number = generate_number_by_column(third_number_ranges)
            
            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number >= third_number:
                    second_number = generate_number_by_column(second_number_ranges)
            
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)
                while first_number >= second_number:
                    first_number = generate_number_by_column(first_number_ranges)
        
        for _ in range(0, 10):
            cash_ball = generate_number_by_column(cash_ball_number_ranges)

        save_generation(
            first=first_number,
            second=second_number,
            third=third_number,
            fourth=fourth_number,
            fifth=fifth_number,
            powerball=cash_ball
        )

    return {}


@app.route("/test/powerball/numbers")
def test_powerball_numbers():
    def number_sort(map):
        return map["percent"]

    number_mapping = []
    for num in range(1, 69):
        count, percent = list(fetch_occurance_by_number(
            num, 
            '2023-05-27'
        ))[0]
        print(count)
        if count > 0:
            number_mapping.append({ "num": num, "percent": percent, "count": count })
    
    number_mapping.sort(key=number_sort)
    return { "numbers": number_mapping }


@app.route("/test/cash4life/numbers")
def test_cash_4_life_numbers():
    def number_sort(map):
        return map["percent"]

    number_mapping = []
    for num in range(1, 61):
        count, percent = list(cash_4_life_fetch_occurance_by_num(num, '2025-04-27'))[0]
        if count > 0:
            number_mapping.append({ "num": num, "percent": percent, "count": count })
    
    number_mapping.sort(key=number_sort)
    return { "numbers": number_mapping }



@app.route("/test/random")
def test_random():
    range_date = request.args.get("start_date", "2023-05-27")
    first_number_ranges = list(cash_4_life_fetch_occurance_by_ball("first_ball", range_date))
    second_number_ranges = list(cash_4_life_fetch_occurance_by_ball("second_ball", range_date))
    third_number_ranges = list(cash_4_life_fetch_occurance_by_ball("third_ball", range_date))
    fourth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fourth_ball", range_date))
    fifth_number_ranges = list(cash_4_life_fetch_occurance_by_ball("fifth_ball", range_date))
    cash_ball_number_ranges = list(cash_4_life_fetch_occurance_by_ball("cash_ball", range_date))
    all_drawings = list(get_all_drawings())
    found_v3_drawing = False
    v3_generation_count = 0

    i = 0
    while found_v3_drawing is False:
        if i % 2 == 0:
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)

            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number <= first_number:
                    second_number = generate_number_by_column(second_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number <= second_number:
                    third_number = generate_number_by_column(third_number_ranges)

            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number <= third_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
                while fifth_number <= fourth_number:
                    fifth_number = generate_number_by_column(fifth_number_ranges)
        else:
            for _ in range(0, 10):
                fifth_number = generate_number_by_column(fifth_number_ranges)
            
            for _ in range(0, 10):
                fourth_number = generate_number_by_column(fourth_number_ranges)
                while fourth_number >= fifth_number:
                    fourth_number = generate_number_by_column(fourth_number_ranges)

            for _ in range(0, 10):
                third_number = generate_number_by_column(third_number_ranges)
                while third_number >= fourth_number:
                    third_number = generate_number_by_column(third_number_ranges)
            
            for _ in range(0, 10):
                second_number = generate_number_by_column(second_number_ranges)
                while second_number >= third_number:
                    second_number = generate_number_by_column(second_number_ranges)
            
            for _ in range(0, 10):
                first_number = generate_number_by_column(first_number_ranges)
                while first_number >= second_number:
                    first_number = generate_number_by_column(first_number_ranges)

        for _ in range(0, 10):
            cash_ball = generate_number_by_column(cash_ball_number_ranges)

        existing_drawing = None
        # for drawing in all_drawings:
        #     if drawing.first_ball == first_number and \
        #     drawing.second_ball == second_number and \
        #         drawing.third_ball == third_number and \
        #             drawing.fourth_ball == fourth_number and \
        #                 drawing.fifth_ball == fifth_number and \
        #                 drawing.cash_ball == cash_ball:
        #         existing_drawing = drawing

        if first_number == 9 and second_number == 36 and third_number == 44 and fourth_number == 53 and fifth_number == 59 and cash_ball == 3:
            existing_drawing = True

        if existing_drawing:
            found_v3_drawing = True

        v3_generation_count += 1
        if v3_generation_count % 100000 == 0:
            print(v3_generation_count)
        i += 1

    return { 
        "v3_count": v3_generation_count,
    }


@app.teardown_appcontext
def remove_session(exception=None):
    tear_down_db()


if __name__ == "__main__":
    app.run()
