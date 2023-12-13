from fastapi import FastAPI
from fastapi import status
import uvicorn 


app = FastAPI()

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message":"Hello World"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000,
                reload=True)
