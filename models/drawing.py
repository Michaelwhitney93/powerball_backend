from sqlalchemy import Column, Integer, DateTime, Boolean, String
from datetime import datetime
from db.engine import Base


class Drawing(Base):
    __tablename__ = "drawings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_ball = Column(Integer)
    second_ball = Column(Integer)
    third_ball = Column(Integer)
    fourth_ball = Column(Integer)
    fifth_ball = Column(Integer)
    power_ball = Column(Integer)
    date_drawn = Column(DateTime)
    winner = Column(Boolean)
    day_of_week = Column(Integer)
    winner_state = Column(String)

    def __init__(
        self,
        first_ball: int = None,
        second_ball: int = None,
        third_ball: int = None,
        fourth_ball: int = None,
        fifth_ball: int = None,
        power_ball: int = None,
        date_drawn: datetime = None,
        winner: bool = None,
        day_of_week: int = None,
        winner_state: str = None,
    ):
        self.first_ball = first_ball
        self.second_ball = second_ball
        self.third_ball = third_ball
        self.fourth_ball = fourth_ball
        self.fifth_ball = fifth_ball
        self.power_ball = power_ball
        self.date_drawn = date_drawn
        self.winner = winner
        self.day_of_week = day_of_week
        self.winner_state = winner_state

    def is_complete_instance(self):
        if (
            self.first_ball is None
            or self.second_ball is None
            or self.third_ball is None
            or self.fourth_ball is None
            or self.fifth_ball is None
            or self.power_ball is None
        ):
            return False

        return True