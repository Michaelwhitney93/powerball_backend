import requests
from flask import Flask, request
from db.engine import init_db, tear_down_db
from controllers.power_ball.populate_v1 import populate_power_ball_drawings
from controllers.cash_4_life.populate_v1 import populate_cash_4_life_drawings
from controllers.power_ball.generate_v1 import generate_power_ball_drawing_v1
from controllers.power_ball.generate_v2 import generate_power_ball_drawing_v2
from controllers.power_ball.generate_v3 import generate_power_ball_drawing_v3
from controllers.power_ball.generate_v4 import generate_power_ball_drawing_v4, generate_power_ball_drawing_overtime_v4
from controllers.cash_4_life.generate_v4 import generate_cash_4_life_drawing_v4, generate_cash_4_life_drawing_overtime_v4


app = Flask(__name__)

init_db()

@app.route("/")
def default():
    return "<p>Hello World!</p>"


@app.route("/drawings/powerball")
def get_power_ball_drawings():
    try:
        populate_power_ball_drawings()
        return {}
    except requests.exceptions.RequestException as e:
        return f"Request Failed: {e}", 500


@app.route("/drawings/cash4life")
def get_cash_4_life_drawings():
    try:
        populate_cash_4_life_drawings()
        return {}
    except requests.exceptions.RequestException as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/overtime/v4")
def generate_powerball_numbers_over_time():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        return generate_power_ball_drawing_overtime_v4(drawing_count)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/cash4life/overtime/v4")
def generate_cash_4_life_numbers_over_time():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        return generate_cash_4_life_drawing_overtime_v4(drawing_count)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/random/v1")
def generate_random_drawing_v1():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        return generate_power_ball_drawing_v1(drawing_count)
    except Exception as e:
        return f"Request Failed: {e}", 500

@app.route("/generate/powerball/random/v2")
def generate_random_drawing_v2():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        return generate_power_ball_drawing_v2(drawing_count, should_save_generation)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/random/v3")
def generate_random_drawing_v3():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        range_date = request.args.get("start_date", "2015-10-03")
        return generate_power_ball_drawing_v3(drawing_count, should_save_generation, range_date)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/random/v4")
def generate_random_powerball_drawing_v4():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        range_date = request.args.get("start_date", "2015-10-03")
        return generate_power_ball_drawing_v4(drawing_count, should_save_generation, range_date)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/cash_4_life/random/v4")
def generate_random_cash4life_drawing_v4():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        range_date = request.args.get("start_date", "2014-06-16")
        return generate_cash_4_life_drawing_v4(drawing_count, range_date)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.teardown_appcontext
def remove_session(exception=None):
    tear_down_db()


if __name__ == "__main__":
    app.run()
