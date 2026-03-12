from sqlalchemy import Column, Integer, String, Boolean, Float
from app.core.database import Base


class Comment(Base):

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    video_id = Column(String, index=True)

    text = Column(String)

    spam = Column(Boolean)

    score = Column(Float)