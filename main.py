from fastapi import FastAPI
from fastapi import status
from pydantic import BaseModel

import sqlalchemy
import uvicorn 

metadata = sqlalchemy.MetaData()

boards = sqlalchemy.Table(
    "boards",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
)

class Board(BaseModel):
    name: str
    description: str | None = None

app = FastAPI()

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message":"Hello World"}

@app.post("/boards", status_code=status.HTTP_201_CREATED)
async def create_board(board: Board):
    query = boards.insert().values(name=board.name, description=board.description)
    
    return board

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000,
                reload=True)
