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


def test_retrieve_board():
    test_create_board()
    response = client.get("/boards/"+"1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["description"] == ""

def test_retrieve_board_not_exist():
    time_sec = time.time()
    response = client.get("/boards/"+str(time_sec))
    assert response.status_code == 400


def test_retrieve_all_boards():
    test_create_board()
    response = client.get("/boards/")
    print('go')
    print(response.__dict__)
    assert response.status_code == 200

def test_retrieve_all_empty_boards():
    pass