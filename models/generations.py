from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from db.engine import Base


class Generation(Base):
    __tablename__ = "generations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_ball = Column(Integer)
    second_ball = Column(Integer)
    third_ball = Column(Integer)
    fourth_ball = Column(Integer)
    fifth_ball = Column(Integer)
    power_ball = Column(Integer)
    date_generated = Column(DateTime)

    def __init__(
        self,
        first_ball: int = None,
        second_ball: int = None,
        third_ball: int = None,
        fourth_ball: int = None,
        fifth_ball: int = None,
        power_ball: int = None,
        date_generated: datetime = None
    ):
        self.first_ball=first_ball
        self.second_ball=second_ball
        self.third_ball=third_ball
        self.fourth_ball=fourth_ball
        self.fifth_ball=fifth_ball
        self.power_ball=power_ball
        self.date_generated=date_generated
