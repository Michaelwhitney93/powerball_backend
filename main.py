import random
import requests
from flask import Flask
from db.engine import init_db, tear_down_db
from services.fetch_numbers_service.fetch_numbers import populate_drawings, check_numbers

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
    first_number = random.randint(1, 14)
    second_number = random.randint(max(first_number + 1, 12), 32)
    third_number = random.randint(max(second_number + 1, 21), 47)
    fourth_number = random.randint(max(third_number + 1, 36), 63)
    fifth_number = random.randint(max(fourth_number + 1, 58), 69)
    powerball_number = random.randint(1, 26)

    existing_drawing = check_numbers(first_number, second_number, third_number, fourth_number, fifth_number, powerball_number)

    return {
        "numbers": [
            {"first_number": first_number},
            {"second_number": second_number},
            {"third_number": third_number},
            {"fourth_number": fourth_number},
            {"fifth_number": fifth_number},
            {"powerball_number": powerball_number}
        ],
        "drawn_before": True if existing_drawing else False,
    }


@app.teardown_appcontext
def remove_session(exception=None):
    tear_down_db()


if __name__ == "__main__":
    app.run()
