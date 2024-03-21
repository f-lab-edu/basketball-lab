import uvicorn
from typing import List 
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas, database

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message":"Hello World"}

@app.post("/boards/", status_code=status.HTTP_201_CREATED, response_model=schemas.BoardResponse)
async def create_board(board: schemas.BoardRequest, db: Session = Depends(get_db)):
    db_board = crud.get_board_by_name(db, name=board.name)
    if db_board:
        raise HTTPException(status_code=400, detail="Board with this name already exist")
    return crud.create_board(db=db, board=board)

@app.get("/boards/{boardId}", status_code=status.HTTP_200_OK, response_model=schemas.BoardResponse)
async def retrieve_board(boardId: int, db: Session = Depends(get_db)):
    db_board = crud.get_board_by_id(db, id=boardId)
    if db_board is None:
        raise HTTPException(status_code=404, detail="Board with this ID does not exist")
    return db_board

@app.get("/boards/", status_code=status.HTTP_200_OK, response_model=List[schemas.BoardResponse])
async def retrieve_all_boards(db: Session = Depends(get_db)):
    db_board = crud.get_all_boards(db)
    if db_board is None:
        raise HTTPException(status_code=400, detail="Boards do not exist")
    return db_board

@app.patch("/boards/{boardId}", status_code=status.HTTP_200_OK, response_model=schemas.BoardResponse)    
async def modify_board(boardId: int, board: schemas.BoardRequest, db: Session = Depends(get_db)):
    db_board_by_id = crud.get_board_by_id(db, id=boardId)
    if db_board_by_id is None:
        raise HTTPException(status_code=404, detail="Board with this ID does not exist")
    
    if board.name and board.name != db_board_by_id.name:
        db_board_by_name = crud.get_board_by_name(db, name=board.name)
        if db_board_by_name:
            raise HTTPException(status_code=400, detail="Board with this name already does not exist")
        db_board_by_id.name = board.name
    
    if board.description:
        db_board_by_id.description = board.description

    db.commit()
    db.refresh(db_board_by_id)

    return db_board_by_id


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000,
                reload=True)
