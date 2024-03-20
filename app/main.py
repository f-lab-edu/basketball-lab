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
        raise HTTPException(status_code=400, detail="Board with this name already exists")
    return crud.create_board(db=db, board=board)

@app.get("/boards/{boardId}", status_code=status.HTTP_200_OK, response_model=schemas.BoardResponse)
async def retrieve_board(boardId, db: Session = Depends(get_db)):
    db_board = crud.get_board_by_id(db, id=boardId)
    if not db_board:
        raise HTTPException(status_code=400, detail="Board with this ID not exists")
    return db_board

@app.get("/boards/", status_code=status.HTTP_200_OK, response_model=List[schemas.BoardResponse])
async def retrieve_all_boards(db: Session = Depends(get_db)):
    db_board = crud.get_all_boards(db)
    if not db_board:
        raise HTTPException(status_code=400, detail="Boards not exist")
    return db_board
    

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000,
                reload=True)
