from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from app.core.database import Base


class Comment(Base):

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    youtube_comment_id = Column(String, unique=True, index=True, nullable=True)
    video_id = Column(String, index=True)
    discovery_query = Column(String, index=True, nullable=True)
    text = Column(Text, nullable=False)
    author = Column(String, nullable=True)
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), nullable=True)
    spam = Column(Boolean, default=False)
    score = Column(Float, default=0)
    ml_score = Column(Float, default=0)
    detection_reasons = Column(Text, nullable=True)
    moderation_status = Column(String, default="pending")
    was_deleted = Column(Boolean, default=False)
