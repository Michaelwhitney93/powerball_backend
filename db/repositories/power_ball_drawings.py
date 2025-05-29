from sqlalchemy import text
from models.drawing import Drawing
from db.engine import engine


class PowerballRepository:
    @classmethod
    def get_by(cls, **kwargs):
        return Drawing.query.filter_by(**kwargs).first()

    @classmethod
    def get_all_drawings(cls):
        return Drawing.query.all()

    @classmethod
    def fetch_occurance_by_ball_position(cls, column, date):
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    f"""
                    SELECT {column}, COUNT(DISTINCT(id)) as count, CAST(COUNT(DISTINCT(id)) as float) / (
                            SELECT COUNT(*)
                            FROM drawings
                            WHERE date_drawn >= '{date}'
                    ) as percent
                    FROM drawings
                    WHERE date_drawn >= '{date}'
                    GROUP BY {column}
                    ORDER BY count DESC
                    """
                )
            )
            return result

    @classmethod
    def fetch_occurance_by_number(cls, date='2015-10-03'):
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    f"""
                    SELECT
                    n.num AS number,
                    COUNT(*) AS count,
                    CAST(COUNT(*) AS FLOAT) / (t.total_draws * 5) AS percent
                    FROM (
                        SELECT first_ball AS num FROM drawings WHERE date_drawn >= '{date}'
                        UNION ALL
                        SELECT second_ball FROM drawings WHERE date_drawn >= '{date}'
                        UNION ALL
                        SELECT third_ball FROM drawings WHERE date_drawn >= '{date}'
                        UNION ALL
                        SELECT fourth_ball FROM drawings WHERE date_drawn >= '{date}'
                        UNION ALL
                        SELECT fifth_ball FROM drawings WHERE date_drawn >= '{date}'
                    ) n,
                    (
                        SELECT COUNT(*) AS total_draws
                        FROM drawings
                        WHERE date_drawn >= '{date}'
                    ) t
                    GROUP BY n.num, t.total_draws
                    ORDER BY percent;
                    """
                )
            )
            return result
