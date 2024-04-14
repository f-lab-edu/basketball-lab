from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class Board(Base):
    __tablename__ = 'boards'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    author = Column(String, index=True)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    board_id = Column(Integer, ForeignKey('boards.id'))

    board = relationship("Board", back_populates="posts")

Board.posts = relationship("Post", order_by=Post.id, back_populates="board")
