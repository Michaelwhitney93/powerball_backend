from sqlalchemy import Column, Integer, ForeignKey
from db.engine import Base


class DrawingMetadata(Base):
    __tablename__ = "drawing_metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    drawing_id = Column(Integer, ForeignKey("drawings.id"), nullable=False)

    def __init__(self, drawing_id: int = None):
        self.drawing_id = drawing_id
