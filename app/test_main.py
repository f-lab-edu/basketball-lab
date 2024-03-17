from fastapi.testclient import TestClient
from app.main import app
import time 

client = TestClient(app)

def test_create_board():
    time_sec = time.time() 
    response = client.post("/boards/", json={
        "name": "board"+str(time_sec),
        "description": ""
    })
    assert response.status_code == 201
    #print(response.__dict__)
    assert response.json()["name"] == "board"+str(time_sec)
    assert response.json()["description"] == ""

def test_create_board_name_duplicate():
    response1 = client.post("/boards/", json={
        "name": "board",
        "description": ""
    })
    response2 = client.post("/boards/", json={
        "name": "board",
        "description": ""
    })
    assert response2.status_code == 400