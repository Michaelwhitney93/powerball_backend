from sqlalchemy import text
from models.drawing import Drawing
from db.engine import engine


def get_by(**kwargs):
    return Drawing.query.filter_by(**kwargs).first()


def get_all_drawings():
    return Drawing.query.all()


def fetch_occurance_by_ball_position(column):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                f"""
                SELECT COUNT(DISTINCT(id)) as count, CAST(COUNT(DISTINCT(id)) as float) / (
                        SELECT COUNT(*)
                        FROM drawings
                        WHERE date_drawn >= '2015-10-07'
                ) as percent, {column}
                FROM drawings
                WHERE date_drawn >= '2015-10-07'
                GROUP BY {column}
                ORDER BY count DESC
                """
            )
        )
        return result


def fetch_occurance_by_number(number):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                f"""
                SELECT COUNT(DISTINCT(id)) as count, CAST(COUNT(DISTINCT(id)) as float) / (
                        SELECT COUNT(*)
                        FROM drawings
                        WHERE date_drawn >= '2015-10-03' AND date_drawn <= '2020-10-03'
                ) as percent
                FROM drawings
                WHERE (first_ball = {number} OR second_ball = {number} OR third_ball = {number} OR fourth_ball = {number} OR fifth_ball = {number}) AND (date_drawn >= '2015-10-03')
                """
            )
        )
        return result