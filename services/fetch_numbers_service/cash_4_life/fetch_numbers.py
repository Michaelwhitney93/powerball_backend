import requests
import json
import time
import random
from datetime import datetime, timedelta
from services.fetch_numbers_service.constants import CASH_4_LIFE_START_DRAWING_DATE
from db.engine import db_session
from db.repositories.cash_4_life_drawings import Cash4LifeRepository
from models.generations import Generation
from models.cash_4_life_drawing import Cash4LifeDrawing
    

def populate_drawings(start_date: str = CASH_4_LIFE_START_DRAWING_DATE):
    try:
        while datetime.strptime(start_date, "%Y-%m-%d") < datetime.today():
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            epoch_start = int(start_datetime.timestamp() * 1000)
            two_years_timedelta = timedelta(730)
            end_datetime = start_datetime + two_years_timedelta
            epoch_end = int(end_datetime.timestamp() * 1000)

            response = requests.get(
                f"https://www.njlottery.com/api/v1/draw-games/draws/page?status=CLOSED&size=2000&page=0&game-names=Cash%204%20Life&date-to={epoch_end}&date-from={epoch_start}"
            )
            response.raise_for_status()
            response_body = json.loads(response.text)

            for draw in response_body["draws"]:
                drawing = draw["results"][0]["primary"]
                date_drawn = datetime.fromtimestamp(draw['drawTime'] / 1000.0)
                first_ball = int(drawing[0])
                second_ball = int(drawing[1])
                third_ball = int(drawing[2])
                fourth_ball = int(drawing[3])
                fifth_ball = int(drawing[4])
                cash_ball = int("".join(drawing[5].split("-")[1]))
                cash_4_life_drawing = Cash4LifeDrawing(
                    first_ball=first_ball,
                    second_ball=second_ball,
                    third_ball=third_ball,
                    fourth_ball=fourth_ball,
                    fifth_ball=fifth_ball,
                    cash_ball=cash_ball,
                    date_drawn=date_drawn
                )
                if cash_4_life_drawing.is_complete_instance():
                    print(cash_4_life_drawing.date_drawn)
                    existing_drawing = Cash4LifeRepository.get_by(date_drawn=cash_4_life_drawing.date_drawn)
                    if not existing_drawing:
                        print("Saving")
                        db_session.add(cash_4_life_drawing)
                        db_session.commit()
            start_date = datetime.fromtimestamp(epoch_end / 1000.0).strftime("%Y-%m-%d")
            backoff_time = random.uniform(1, 20)
            time.sleep(backoff_time)
    except requests.exceptions.RequestException as e:
        print(f"Request Failed: {e}")
        raise e
    

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


def check_numbers(first, second, third, fourth, fifth, cash_ball=None):
    kwargs = dict(
        first_ball=first,
        second_ball=second,
        third_ball=third,
        fourth_ball=fourth,
        fifth_ball=fifth
    )
    if cash_ball:
        kwargs["cash_ball"] = cash_ball
    existing_drawing = Cash4LifeRepository.get_by(**kwargs)
    return existing_drawing
