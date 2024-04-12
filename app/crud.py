from sqlalchemy.orm import Session
from . import models, schemas

def create_board(db: Session, board: schemas.BoardRequest):
    db_board = models.Board(name=board.name, description=board.description)
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board

def get_board_by_name(db: Session, name: str):
    return db.query(models.Board).filter(models.Board.name == name).first()

def get_board_by_id(db: Session, id: int):
    return db.query(models.Board).filter(models.Board.id == id).first()

def get_all_boards(db: Session):
    return db.query(models.Board).all() # all method returns lists only, not None

def delete_board(db: Session, id:int):
    return db.query(models.Board).filter(models.Board.id == id).delete()
