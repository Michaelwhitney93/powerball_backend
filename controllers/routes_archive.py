from flask import Blueprint, request
from controllers.generate_archive import (
    generate_powerball_drawing_v1, generate_powerball_drawing_v2,
    generate_powerball_drawing_v3, generate_powerball_drawing_v4, generate_powerball_drawing_v5,
    generate_powerball_drawing_overtime
)

archive_bp = Blueprint("archive", __name__)


@archive_bp.route("/generate/powerball/overtime")
def generate_powerball_numbers_over_time():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        return generate_powerball_drawing_overtime(drawing_count)
    except Exception as e:
        return f"Request Failed: {e}", 500


@archive_bp.route("/generate/powerball/random/v1")
def generate_random_drawing_v1():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        return generate_powerball_drawing_v1(drawing_count)
    except Exception as e:
        return f"Request Failed: {e}", 500


@archive_bp.route("/generate/powerball/random/v2")
def generate_random_drawing_v2():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        return generate_powerball_drawing_v2(drawing_count, should_save_generation)
    except Exception as e:
        return f"Request Failed: {e}", 500


@archive_bp.route("/generate/powerball/random/v3")
def generate_random_drawing_v3():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        range_date = request.args.get("start_date", "2015-10-03")
        return generate_powerball_drawing_v3(drawing_count, should_save_generation, range_date)
    except Exception as e:
        return f"Request Failed: {e}", 500


@archive_bp.route("/generate/powerball/random/v4")
def generate_random_drawing_v4():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        range_date = request.args.get("start_date", "2015-10-03")
        return generate_powerball_drawing_v4(drawing_count, should_save_generation, range_date)
    except Exception as e:
        return f"Request Failed: {e}", 500


@archive_bp.route("/generate/powerball/random/v5")
def generate_random_drawing_v5():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        return generate_powerball_drawing_v5(drawing_count, should_save_generation)
    except Exception as e:
        return f"Request Failed: {e}", 500
