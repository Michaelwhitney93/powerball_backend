import random
import requests
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from constants import LAST_BALL_COUNT_CHANGE_DATE, MONDAY_DRAWING_START_DATE
from services.parser import build_drawing_from_html
from db.engine import Base


TWO_DRAWING_DAYS = {2, 5}    # Wednesday, Saturday
THREE_DRAWING_DAYS = {0, 2, 5}  # Monday, Wednesday, Saturday

MONDAY_DRAWING_START = date.fromisoformat(MONDAY_DRAWING_START_DATE)


def random_drawing_date():
    start = date.fromisoformat(LAST_BALL_COUNT_CHANGE_DATE) + timedelta(days=1)
    end = date(2024, 12, 31)
    delta = (end - start).days
    while True:
        candidate = start + timedelta(days=random.randint(0, delta))
        valid_days = THREE_DRAWING_DAYS if candidate >= MONDAY_DRAWING_START else TWO_DRAWING_DAYS
        if candidate.weekday() in valid_days:
            return candidate


def test_fetch_parse_and_save():
    draw_date = random_drawing_date()
    draw_date_str = draw_date.strftime("%Y-%m-%d")

    response = requests.get(
        f"https://www.powerball.com/draw-result?gc=powerball&date={draw_date_str}"
    )
    assert response.status_code == 200, f"Request failed for {draw_date_str}"

    drawing = build_drawing_from_html(response.text)

    assert drawing.date_drawn.date() == draw_date, (
        f"Date mismatch: requested {draw_date}, received {drawing.date_drawn.date()}"
    )
    assert drawing.is_complete_instance(), f"Incomplete drawing returned for {draw_date_str}"
    assert 1 <= drawing.first_ball <= 69
    assert 1 <= drawing.second_ball <= 69
    assert 1 <= drawing.third_ball <= 69
    assert 1 <= drawing.fourth_ball <= 69
    assert 1 <= drawing.fifth_ball <= 69
    assert 1 <= drawing.power_ball <= 26
    assert drawing.day_of_week == draw_date.weekday()
    assert isinstance(drawing.winner, bool)
    if drawing.winner:
        assert drawing.winner_state is not None
        assert len(drawing.winner_state) == 2
    else:
        assert drawing.winner_state is None

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = scoped_session(sessionmaker(bind=engine))

    session.add(drawing)
    session.commit()

    saved = session.query(drawing.__class__).filter_by(date_drawn=drawing.date_drawn).first()
    assert saved is not None
    assert saved.first_ball == drawing.first_ball
    assert saved.power_ball == drawing.power_ball
    assert saved.day_of_week == drawing.day_of_week
    assert saved.winner == drawing.winner
    assert saved.winner_state == drawing.winner_state

    session.remove()
