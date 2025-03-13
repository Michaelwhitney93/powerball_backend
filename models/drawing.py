from sqlalchemy import Column, Integer, Date
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
    date_drawn = Column(Date)

    def __init__(
        self,
        first_ball=None,
        second_ball=None,
        third_ball=None,
        fourth_ball=None,
        fifth_ball=None,
        power_ball=None,
        date_drawn=None
    ):
        self.first_ball=first_ball
        self.second_ball=second_ball
        self.third_ball=third_ball
        self.fourth_ball=fourth_ball
        self.fifth_ball=fifth_ball
        self.power_ball=power_ball
        self.date_drawn=date_drawn
