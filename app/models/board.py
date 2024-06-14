from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.post import Post

class Board(Base):
    __tablename__ = 'boards'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)

    posts = relationship("Post", order_by=Post.id, back_populates="board")

