import random
import requests
import math
from flask import Flask, request
from db.engine import init_db, tear_down_db
from db.repositories.drawings import fetch_occurance_by_ball_position
from services.fetch_numbers_service.fetch_numbers import populate_drawings, check_numbers, save_generation
from services.fetch_numbers_service.constants import NUMBER_GENERATION_RANGE, ALT_CHANGE_RANGE
from services.generate_numbers_service.v3_generate import generate_number_by_column, get_occurance_by_number
from db.repositories.generations import get_all

app = Flask(__name__)
init_db()


@app.route("/")
def default():
    return "<p>Hello World!</p>"


@app.route("/drawings")
def get_drawings():
    try:
        populate_drawings()
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


@app.route("/generate/random/v3")
def generate_random_drawing_v3():
    drawing_count = int(request.args.get("drawings", "1"))
    should_save_generation = request.args.get("save_generation", "False") == "True"
    numbers = []
    existing_drawing = False
    first_number_ranges = list(fetch_occurance_by_ball_position("first_ball"))
    second_number_ranges = list(fetch_occurance_by_ball_position("second_ball"))
    third_number_ranges = list(fetch_occurance_by_ball_position("third_ball"))
    fourth_number_ranges = list(fetch_occurance_by_ball_position("fourth_ball"))
    fifth_number_ranges = list(fetch_occurance_by_ball_position("fifth_ball"))
    power_ball_number_ranges = list(fetch_occurance_by_ball_position("power_ball"))
    for _ in range(drawing_count):
        # first_number = generate_number_by_column("first_ball")

        # second_number = generate_number_by_column("second_ball")
        # while second_number <= first_number:
        #     second_number = generate_number_by_column("second_ball")

        # third_number = generate_number_by_column("third_ball")
        # while third_number <= second_number:
        #     third_number = generate_number_by_column("third_ball")

        # fourth_number = generate_number_by_column("fourth_ball")
        # while fourth_number <= third_number:
        #     fourth_number = generate_number_by_column("fourth_ball")

        # fifth_number = generate_number_by_column("fifth_ball")
        # while fifth_number <= fourth_number:
        #     fifth_number = generate_number_by_column("fifth_ball")
        for _ in range(0, 10):
            first_number = generate_number_by_column(first_number_ranges)

        for _ in range(0, 10):
            fifth_number = generate_number_by_column(fifth_number_ranges)
            while fifth_number <= first_number + 12:
                fifth_number = generate_number_by_column(fifth_number_ranges)

        for _ in range(0, 10):
            second_number = generate_number_by_column(second_number_ranges)
            while second_number <= first_number or second_number + 3 >= fifth_number:
                second_number = generate_number_by_column(second_number_ranges)

        for _ in range(0, 10):
            fourth_number = generate_number_by_column(fourth_number_ranges)
            while fourth_number <= second_number + 2 or fourth_number >= fifth_number:
                fourth_number = generate_number_by_column(fourth_number_ranges)

        for _ in range(0, 10):
            third_number = generate_number_by_column(third_number_ranges)
            while third_number <= second_number or third_number >= fourth_number:
                third_number = generate_number_by_column(third_number_ranges)

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
    v1_count_avg = 0
    v3_count_avg = 0
    first_number_range = list(fetch_occurance_by_ball_position("first_ball"))
    for _ in range(1, 100):
        v1_generations = []
        v3_generations = []
        v1_count = 0
        v3_count = 0
        for _ in range(0, 1179):
            generation = []
            for _ in range(0, 5):
                number = random.randint(1,69)
                generation.append(number)
            v1_generations.append(generation)

            first_number = generate_number_by_column(first_number_range)
            v3_generations.append([first_number])

        for gen in v1_generations:
            sorted_gen = sorted(gen)
            if sorted_gen[0] == 13:
                v1_count += 1
        
        for gen in v3_generations:
            sorted_gen = sorted(gen)
            if sorted_gen[0] == 13:
                v3_count += 1
        print(v1_count)
        v1_count_avg += abs(v1_count - 27)
        v3_count_avg += abs(v3_count - 27)

    return {
         "v1_generation_count_avg": v1_count_avg / 100,
         "v3_generation_count_avg": v3_count_avg / 100
    }



@app.route("/test/random")
def test_random():
    drawings_per_number = []
    for num in range(1, 70):
        query = list(get_occurance_by_number(num))
        drawings_per_number.append({
            "number": str(num),
            "count": query[0][0],
            "percent": query[0][1]
        })
    
    def sort_by_percent(drawing):
        return drawing["percent"]

    drawings_per_number.sort(key=sort_by_percent)

    return { "drawings": drawings_per_number }

@app.teardown_appcontext
def remove_session(exception=None):
    tear_down_db()


if __name__ == "__main__":
    app.run()
