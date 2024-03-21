from fastapi.testclient import TestClient
from app.main import app
import time 

client = TestClient(app)

def create_board_name_and_response(id=0):
    time_sec = int(time.time())
    response = client.post("/boards/", json={
        "name": "board"+str(time_sec),
        "description": ""
    })
    return time_sec, response 

def test_create_board():
    time_sec, response = create_board_name_and_response()
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
    _, _ = create_board_name_and_response()
    response = client.get("/boards/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["description"] == ""

def test_retrieve_board_not_exist():
    time_sec = int(time.time())
    response = client.get("/boards/"+str(time_sec))
    assert response.status_code == 404


def test_retrieve_all_boards():
    _, response = create_board_name_and_response()
    response = client.get("/boards/")
    assert response.status_code == 200

def test_retrieve_all_empty_boards():
    pass


def test_modify_board():
    time.sleep(1) #test 중에 int(time.time())의 값이 같은 경우가 있어 
                  #결과적으로 create_board_name_and_response의 예외가 발생함.
                  #근본적으로 해결할 방법이 없을지 생각해볼 필요 있음.
    _, create_response = create_board_name_and_response()
    print(create_response.json())
    response = client.patch("/boards/"+str(create_response.json()["id"]), json={
        "name": "board_name_modified",
        "description": "this board description is modified"
    })
    assert response.status_code == 200
    assert response.json()["id"] == create_response.json()["id"]
    assert response.json()["name"] == "board_name_modified"
    assert response.json()["description"] == "this board description is modified"
