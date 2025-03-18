import requests
import time
import random
from datetime import datetime, timedelta
from services.fetch_numbers_service.constants import NEXT_START_DATE, NEXT_WEEKDAY_DRAWING_MAPPING
from services.fetch_numbers_service.parser import build_drawing_from_html
from db.engine import db_session
from db.repositories.drawings import get_by


def populate_drawings(draw_date: str = NEXT_START_DATE):
    try:
        while datetime.strptime(draw_date, "%Y-%m-%d") <= datetime.today():
            response = requests.get(f"https://www.powerball.com/draw-result?gc=powerball&date={draw_date}")
            response.raise_for_status()
            powerball_drawing = build_drawing_from_html(response.text)
            if powerball_drawing.is_complete_instance():
                print(powerball_drawing.date_drawn)
                existing_drawing = get_by(date_drawn=powerball_drawing.date_drawn)
                if not existing_drawing:
                    print("Saving")
                    db_session.add(powerball_drawing)
                    db_session.commit()
            time_delta = timedelta(NEXT_WEEKDAY_DRAWING_MAPPING.get(powerball_drawing.date_drawn.weekday()))
            new_draw_datetime = datetime.strptime(draw_date, "%Y-%m-%d") + time_delta
            draw_date = new_draw_datetime.strftime("%Y-%m-%d")
            backoff_time = random.uniform(1, 20)
            time.sleep(backoff_time)
    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {e}")
        raise e


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
    existing_drawing = get_by(**kwargs)
    return existing_drawing