from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from db.engine import Base


class Cash4LifeDrawing(Base):
    __tablename__ = "cash_4_life_drawings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_ball = Column(Integer)
    second_ball = Column(Integer)
    third_ball = Column(Integer)
    fourth_ball = Column(Integer)
    fifth_ball = Column(Integer)
    cash_ball = Column(Integer)
    date_drawn = Column(DateTime)

    def __init__(
        self,
        first_ball: int = None,
        second_ball: int = None,
        third_ball: int = None,
        fourth_ball: int = None,
        fifth_ball: int = None,
        cash_ball: int = None,
        date_drawn: datetime = None
    ):
        self.first_ball=first_ball
        self.second_ball=second_ball
        self.third_ball=third_ball
        self.fourth_ball=fourth_ball
        self.fifth_ball=fifth_ball
        self.cash_ball=cash_ball
        self.date_drawn=date_drawn

    def is_complete_instance(self):
        if (
            self.first_ball is None
            or self.second_ball is None
            or self.third_ball is None
            or self.fourth_ball is None
            or self.fifth_ball is None
            or self.cash_ball is None
        ):
            return False

        return True