from sqlalchemy import text
from db.engine import engine
from models.cash_4_life_drawing import Cash4LifeDrawing


class Cash4LifeRepository:
    @classmethod
    def get_by(cls, **kwargs):
        return Cash4LifeDrawing.query.filter_by(**kwargs).first()

    @classmethod
    def get_all_drawings(cls):
        return Cash4LifeDrawing.query.all()

    @classmethod
    def fetch_occurance_by_ball_position(cls, column, date):
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    f"""
                    SELECT {column}, COUNT(DISTINCT(id)) as count, CAST(COUNT(DISTINCT(id)) as float) / (
                            SELECT COUNT(*)
                            FROM cash_4_life_drawings
                            WHERE date_drawn >= '{date}'
                    ) as percent
                    FROM cash_4_life_drawings
                    WHERE date_drawn >= '{date}'
                    GROUP BY {column}
                    ORDER BY count DESC
                    """
                )
            )
            return result
        
    @classmethod
    def fetch_occurance_by_number(cls, date='2014-06-16'):
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    f"""
                    SELECT
                    n.num AS number,
                    COUNT(*) AS count,
                    CAST(COUNT(*) AS FLOAT) / (t.total_draws * 5) AS percent
                    FROM (
                        SELECT first_ball AS num FROM cash_4_life_drawings WHERE date_drawn >= '{date}'
                        UNION ALL
                        SELECT second_ball FROM cash_4_life_drawings WHERE date_drawn >= '{date}'
                        UNION ALL
                        SELECT third_ball FROM cash_4_life_drawings WHERE date_drawn >= '{date}'
                        UNION ALL
                        SELECT fourth_ball FROM cash_4_life_drawings WHERE date_drawn >= '{date}'
                        UNION ALL
                        SELECT fifth_ball FROM cash_4_life_drawings WHERE date_drawn >= '{date}'
                    ) n,
                    (
                        SELECT COUNT(*) AS total_draws
                        FROM cash_4_life_drawings
                        WHERE date_drawn >= '{date}'
                    ) t
                    GROUP BY n.num, t.total_draws
                    ORDER BY percent;
                    """
                )
            )
            return result

    @classmethod
    def fetch_occurance_with_num_and_date(cls):
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    f"""
                    SELECT num, date_drawn
                    FROM (
                        SELECT first_ball AS num, date_drawn FROM cash_4_life_drawings
                        UNION ALL
                        SELECT second_ball, date_drawn FROM cash_4_life_drawings
                        UNION ALL
                        SELECT third_ball, date_drawn FROM cash_4_life_drawings
                        UNION ALL
                        SELECT fourth_ball, date_drawn FROM cash_4_life_drawings
                        UNION ALL
                        SELECT fifth_ball, date_drawn FROM cash_4_life_drawings
                    ) all_numbers
                    ORDER BY num, date_drawn;
                    """
                )
            )
            return result
        
    @classmethod
    def fetch_cash_ball_occurance_with_num_and_date(cls):
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    f"""
                    SELECT cash_ball, date_drawn
                    FROM cash_4_life_drawings
                    ORDER BY cash_ball, date_drawn;
                    """
                )
            )
            return result