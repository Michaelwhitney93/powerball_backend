from sqlalchemy import text
from models.drawing import Drawing
from db.engine import engine


def get_by(**kwargs):
    return Drawing.query.filter_by(**kwargs).first()


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


