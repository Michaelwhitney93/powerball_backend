import random
import requests
from flask import Flask, request
from db.engine import init_db, tear_down_db
from services.fetch_numbers_service.fetch_numbers import populate_drawings, check_numbers
from services.fetch_numbers_service.constants import NUMBER_GENERATION_RANGE
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


@app.route("/generate/random")
def generate_random_drawing():
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


@app.route("/test/generations")
def test_generations():
    drawing_count = int(request.args.get("drawings", "1"))
    numbers = []
    for _ in range(drawing_count):
        fits_range = True
        drawn_numbers = set()
        first_number = random.randint(1, 69)
        drawn_numbers.add(first_number)

        second_number = random.randint(1, 69)
        while second_number in drawn_numbers:
            second_number = random.randint(1, 69)
        drawn_numbers.add(second_number)

        third_number = random.randint(1, 69)
        while third_number in drawn_numbers:
            third_number = random.randint(1, 69)
        drawn_numbers.add(third_number)

        fourth_number = random.randint(1, 69)
        while fourth_number in drawn_numbers:
            fourth_number = random.randint(1, 69)
        drawn_numbers.add(fourth_number)

        fifth_number = random.randint(1, 69)
        while fifth_number in drawn_numbers:
            fifth_number = random.randint(1, 69)
        drawn_numbers.add(fifth_number)

        ordered_numbers = sorted([first_number, second_number, third_number, fourth_number, fifth_number])
        if (
            ordered_numbers[0] not in range(NUMBER_GENERATION_RANGE["first_number"][0], NUMBER_GENERATION_RANGE["first_number"][1] + 1) or
            ordered_numbers[1] not in range(NUMBER_GENERATION_RANGE["second_number"][0], NUMBER_GENERATION_RANGE["second_number"][1] + 1) or
            ordered_numbers[2] not in range(NUMBER_GENERATION_RANGE["third_number"][0], NUMBER_GENERATION_RANGE["third_number"][1] + 1) or
            ordered_numbers[3] not in range(NUMBER_GENERATION_RANGE["fourth_number"][0], NUMBER_GENERATION_RANGE["fourth_number"][1] + 1) or
            ordered_numbers[4] not in range(NUMBER_GENERATION_RANGE["fifth_number"][0], NUMBER_GENERATION_RANGE["fifth_number"][1] + 1)
        ):
            fits_range = False
        numbers.append([ordered_numbers, fits_range])

    return {
        "numbers": numbers,
    }


@app.route("/test/drawings")
def test_drawings():
    pass

@app.teardown_appcontext
def remove_session(exception=None):
    tear_down_db()


if __name__ == "__main__":
    app.run()
