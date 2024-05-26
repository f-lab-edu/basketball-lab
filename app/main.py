import io
import json
import pandas as pd 
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated

from . import crud, schemas, database
from app.models.board import Board
from app.models.post import Post
database.Base.metadata.create_all(bind=database.engine)

def get_application() -> FastAPI:
    application = FastAPI()
    return application

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = get_application()

@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> dict:
    return {"message":"Hello World"}

@app.post("/boards/", status_code=status.HTTP_201_CREATED, response_model=schemas.BoardResponse)
async def create_board(board: schemas.BoardRequest, db: Session = Depends(get_db)) -> Board:
    db_board = crud.get_board_by_name(db, name=board.name)
    if db_board:
        raise HTTPException(status_code=400, detail="Board with this name already exist")
    return crud.create_board(db=db, board=board)

@app.get("/boards/{boardId}", status_code=status.HTTP_200_OK, response_model=schemas.BoardResponse)
async def retrieve_board(boardId: int, db: Session = Depends(get_db)) -> Optional[Board]:
    db_board = crud.get_board_by_id(db, id=boardId)
    if db_board is None:
        raise HTTPException(status_code=404, detail="Board with this ID does not exist")
    return db_board

@app.get("/boards/", status_code=status.HTTP_200_OK, response_model=List[schemas.BoardResponse])
async def retrieve_all_boards(db: Session = Depends(get_db)) -> List[Board]:
    db_board = crud.get_all_boards(db)
    if not db_board: # This checks for an empty list as well as None
        raise HTTPException(status_code=404, detail="Boards do not exist")
    return db_board

@app.patch("/boards/{boardId}", status_code=status.HTTP_200_OK, response_model=schemas.BoardResponse)    
async def modify_board(boardId: int, board: schemas.BoardRequest, db: Session = Depends(get_db)) -> Optional[Board]:
    db_board_by_id = crud.get_board_by_id(db, id=boardId)
    if db_board_by_id is None:
        raise HTTPException(status_code=404, detail="Board with this ID does not exist")
    
    if board.name and board.name != db_board_by_id.name:
        db_board_by_name = crud.get_board_by_name(db, name=board.name)
        if db_board_by_name:
            raise HTTPException(status_code=400, detail="Board with this name already exist")
        db_board_by_id.name = board.name
    
    if board.description:
        db_board_by_id.description = board.description

    db.commit()
    db.refresh(db_board_by_id)

    return db_board_by_id

@app.post("/boards/{boardId}/posts/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post(boardId: int, post: schemas.PostRequest, db: Session=Depends(get_db)) -> Post:
    db_board = crud.get_board_by_id(db, id=boardId)
    if db_board is None:
        raise HTTPException(status_code=404, detail="Board with this ID does not exist")
    return crud.create_post(db=db, post=post, board_id=boardId)

@app.get("/boards/{boardId}/posts/{postId}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
async def retrieve_post(boardId: int, postId: int, db: Session=Depends(get_db)) -> Optional[Post]:
    db_board = crud.get_board_by_id(db, id=boardId)
    if db_board is None:
        raise HTTPException(status_code=404, detail="Board with this ID does not exist")
    db_post = crud.get_post_by_id(db, boardId, postId)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post with this ID does not exist")
    return db_post

@app.get("/boards/{boardId}/posts/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostResponse])
async def retrieve_posts(boardId: int, offset: int, limit: int, db: Session=Depends(get_db)) -> List[Post]:
    db_board = crud.get_board_by_id(db, id=boardId)
    if db_board is None:
        raise HTTPException(status_code=404, detail="Board with this ID does not exist")
    db_posts = crud.get_posts_by_board_id(db, board_id=boardId, offset=offset, limit=limit)
    if not db_posts: # This checks for an empty list as well as None
        raise HTTPException(status_code=404, detail="No posts found")
    return db_posts
'''
@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
'''

def parsing_excel_file(file: UploadFile):
    content = file.file.read()
    df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
    data = df.to_dict(orient='records')
    
    with open("log.txt", mode="w", encoding="utf-8") as data_file:
        json.dump(data, data_file, ensure_ascii=False, indent=4)

    return data

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    background_tasks.add_task(parsing_excel_file, file)
    
    return {"message": "File received. Processing in background."}

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000,
                reload=True)

