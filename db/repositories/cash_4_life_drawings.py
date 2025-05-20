from sqlalchemy import text
from db.engine import engine
from models.cash_4_life_drawing import Cash4LifeDrawing

def get_by(**kwargs):
    return Cash4LifeDrawing.query.filter_by(**kwargs).first()


def fetch_occurance_by_ball_position(column):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                f"""
                SELECT COUNT(DISTINCT(id)) as count, CAST(COUNT(DISTINCT(id)) as float) / (
                        SELECT COUNT(*)
                        FROM cash_4_life_drawings
                ) as percent, {column}
                FROM cash_4_life_drawings
                GROUP BY {column}
                ORDER BY count DESC
                """
            )
        )
        return result