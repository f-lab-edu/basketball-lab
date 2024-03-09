from pydantic import BaseModel

class BoardBase(BaseModel):
    name: str
    description: str | None = None

class BoardCreate(BoardBase):
    pass 

class Board(BoardBase):
    id: int

    class Config:
        orm_mode=True
