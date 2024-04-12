from datetime import datetime
from pydantic import BaseModel

class BoardRequest(BaseModel):
    name: str
    description: str | None = None

class BoardResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

class PostRequest(BaseModel):
    title: str
    content: str
    author: int
    timestamp: datetime
    board_id: int

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: int
    timestamp: datetime
    board_id: int 
        
