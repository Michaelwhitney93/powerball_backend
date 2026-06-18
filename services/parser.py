from bs4 import BeautifulSoup
from datetime import datetime
from models.drawing import Drawing


class ParseError(Exception):
    pass


def build_drawing_from_html(html):
    parsed = BeautifulSoup(html, "html.parser")

    date = parsed.find("h5", attrs={"class": "title-date"})
    white_ball_numbers = parsed.find_all("div", attrs={"class": "white-balls"})
    powerball_number = parsed.find("div", attrs={"class": "powerball"})
    winner_location = parsed.find("span", attrs={"class": "winner-location"})

    if not date:
        raise ParseError("Missing date element (title-date)")
    if len(white_ball_numbers) < 5:
        raise ParseError(f"Expected 5 white ball elements, got {len(white_ball_numbers)}")
    if not powerball_number:
        raise ParseError("Missing powerball element")

    date_split = date.text.split(", ")
    month_day_split = date_split[1].split(" ")
    month = month_day_split[0]
    day = month_day_split[1]
    year = date_split[2]

    formatted_date = datetime.strptime(f"{month} {day} {year}", "%b %d %Y")

    winner_state = winner_location.text.strip() if winner_location else None
    had_winner = winner_state is not None and winner_state != "None"

    powerball_drawing = Drawing(
        first_ball=int(white_ball_numbers[0].text),
        second_ball=int(white_ball_numbers[1].text),
        third_ball=int(white_ball_numbers[2].text),
        fourth_ball=int(white_ball_numbers[3].text),
        fifth_ball=int(white_ball_numbers[4].text),
        power_ball=int(powerball_number.text),
        date_drawn=formatted_date,
        winner=had_winner,
        day_of_week=formatted_date.weekday(),
        winner_state=winner_state if had_winner else None,
    )

    return powerball_drawing
