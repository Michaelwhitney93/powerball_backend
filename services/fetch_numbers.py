import requests
import time
import random
from datetime import datetime, timedelta
from constants import NEXT_START_DATE, MONDAY_DRAWING_START_DATE, TWO_DRAWING_WEEKDAY_MAPPING, THREE_DRAWING_WEEKDAY_MAPPING
from services.parser import build_drawing_from_html, ParseError
from db.engine import db_session
from db.repositories.drawings import DrawingsRepository
from models.generations import Generation

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 30


def populate_drawings(draw_date: str = NEXT_START_DATE):
    try:
        while datetime.strptime(draw_date, "%Y-%m-%d") <= datetime.today():
            requested_date = datetime.strptime(draw_date, "%Y-%m-%d")

            powerball_drawing = _fetch_with_retry(draw_date)

            if powerball_drawing is None:
                print(f"Skipping {draw_date}: failed after {MAX_RETRIES} retries")
            elif powerball_drawing.date_drawn.date() != requested_date.date():
                print(f"Date mismatch for {draw_date}: received {powerball_drawing.date_drawn.date()}, skipping")
            elif powerball_drawing.is_complete_instance():
                existing_drawing = DrawingsRepository.get_by(date_drawn=powerball_drawing.date_drawn)
                if not existing_drawing:
                    print(f"Saving {draw_date}")
                    db_session.add(powerball_drawing)
                    db_session.commit()

            mapping = _weekday_mapping_for(requested_date)
            time_delta = timedelta(mapping.get(requested_date.weekday()))
            draw_date = (requested_date + time_delta).strftime("%Y-%m-%d")
            time.sleep(random.uniform(1, 20))

    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {e}")
        raise e


def _weekday_mapping_for(draw_date: datetime):
    monday_start = datetime.strptime(MONDAY_DRAWING_START_DATE, "%Y-%m-%d")
    return THREE_DRAWING_WEEKDAY_MAPPING if draw_date >= monday_start else TWO_DRAWING_WEEKDAY_MAPPING


def _fetch_with_retry(draw_date: str):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                f"https://www.powerball.com/draw-result?gc=powerball&date={draw_date}"
            )
            response.raise_for_status()
            return build_drawing_from_html(response.text)
        except ParseError as e:
            wait = RETRY_BACKOFF_SECONDS * (2 ** attempt)
            print(f"Parse error for {draw_date} (attempt {attempt + 1}/{MAX_RETRIES}): {e}. Retrying in {wait}s")
            time.sleep(wait)
    return None


def save_generation(first, second, third, fourth, fifth, powerball):
    generation = Generation(
        first_ball=first,
        second_ball=second,
        third_ball=third,
        fourth_ball=fourth,
        fifth_ball=fifth,
        power_ball=powerball,
        date_generated=datetime.today()
    )
    db_session.add(generation)
    db_session.commit()


def check_numbers(first, second, third, fourth, fifth, powerball=None):
    kwargs = dict(
        first_ball=first,
        second_ball=second,
        third_ball=third,
        fourth_ball=fourth,
        fifth_ball=fifth
    )
    if powerball:
        kwargs["power_ball"] = powerball
    existing_drawing = DrawingsRepository.get_by(**kwargs)
    return existing_drawing
