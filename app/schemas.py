from pydantic import BaseModel

class BoardRequest(BaseModel):
    name: str
    description: str | None = None

class BoardResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
