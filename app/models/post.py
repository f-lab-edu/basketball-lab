from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    author = Column(String, index=True)
    timestamp = Column(DateTime, index=True, default=datetime.now)
    board_id = Column(Integer, ForeignKey('boards.id'))

    board = relationship("Board", back_populates="posts")

