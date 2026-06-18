import requests
from flask import Flask, request
from db.engine import init_db, tear_down_db
from controllers.populate import populate_powerball_drawings
from controllers.generate import generate_powerball_drawing_v6
from controllers.generate_multi import generate_multi
from controllers.routes_archive import archive_bp


app = Flask(__name__)
app.register_blueprint(archive_bp)

init_db()


@app.route("/")
def default():
    return "<p>Hello World!</p>"


@app.route("/drawings/powerball")
def get_power_ball_drawings():
    try:
        populate_powerball_drawings()
        return {}
    except requests.exceptions.RequestException as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/random")
def generate_random_powerball_drawing():
    try:
        drawing_count = int(request.args.get("drawings", "1"))
        should_save_generation = request.args.get("save_generation", "False") == "True"
        return generate_powerball_drawing_v6(drawing_count, should_save_generation)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.route("/generate/powerball/multi")
def generate_multi_endpoint():
    try:
        count = int(request.args.get("drawings", "1"))
        constraints = [c.strip() for c in request.args.get("constraints", "").split(",") if c.strip()]
        return generate_multi(count, constraints)
    except Exception as e:
        return f"Request Failed: {e}", 500


@app.teardown_appcontext
def remove_session(exception=None):
    tear_down_db()


if __name__ == "__main__":
    app.run()
