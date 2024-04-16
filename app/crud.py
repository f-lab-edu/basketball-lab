from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.board import Board
from app.models.post import Post

from . import schemas

def create_board(db: Session, board: schemas.BoardRequest) -> Board:
    db_board = Board(name=board.name, description=board.description)
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board

def get_board_by_name(db: Session, name: str) -> Optional[Board]:
    return db.query(Board).filter(Board.name == name).first()

def get_board_by_id(db: Session, id: int) -> Optional[Board]:
    return db.query(Board).filter(Board.id == id).first()

def get_all_boards(db: Session) -> List[Board]:
    return db.query(Board).all() # all method returns lists only, not None

def create_post(db: Session, post: schemas.PostRequest, board_id: int) -> Post:
    db_post = Post(title=post.title, content=post.content, author=post.author,
                          board_id=board_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_post(db: Session, board_id: int, post_id:int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id, Post.board_id == board_id).first()