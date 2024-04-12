from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time 
import pytest

from app.database import Base
from app.main import app, get_db

TEST_DATABASE_URL  = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL , connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture(scope="function")
def clear_database():
    # Obtain a new session
    with TestingSessionLocal() as db:
        # Iterate over all tables and delete their contents
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        # Commit the transaction to ensure changes are applied
        db.commit()

def create_board_response(client, offset=0):
    time_sec = int(time.time())+offset
    response = client.post("/boards/", json={
        "name": "board"+str(time_sec),
        "description": ""
    })
    return response 

def test_create_board(client):
    response = create_board_response(client)
    assert response.status_code == 201
    assert response.json()["name"] == response.json()["name"]
    assert response.json()["description"] == ""

def test_create_board_name_already_exist(client):
    response1 = client.post("/boards/", json={
        "name": "board",
        "description": ""
    })
    response2 = client.post("/boards/", json={
        "name": "board",
        "description": ""
    })
    assert response2.status_code == 400

def test_retrieve_board(client):
    create_board_response(client)
    response = client.get("/boards/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["description"] == ""

def test_retrieve_board_id_not_exist(client):
    time_sec = int(time.time())
    response = client.get("/boards/"+str(time_sec))
    assert response.status_code == 404

def test_retrieve_all_boards(client):
    create_board_response(client)
    response = client.get("/boards/")
    assert response.status_code == 200

def test_retrieve_all_boards_not_exist(client, clear_database):
    response = client.get("/boards")
    assert response.status_code == 404

def test_modify_board(client):
    #time.sleep(1) #test 중에 int(time.time())의 값이 같은 경우가 있어 
                  #결과적으로 create_board_name_and_response의 예외가 발생함.
                  #근본적으로 해결할 방법이 없을지 생각해볼 필요 있음.
    create_response = create_board_response(client)
    response = client.patch("/boards/"+str(create_response.json()["id"]), json={
        "name": "board_name_modified",
        "description": "this board description is modified"
    })
    assert response.status_code == 200
    assert response.json()["id"] == create_response.json()["id"]
    assert response.json()["name"] == "board_name_modified"
    assert response.json()["description"] == "this board description is modified"

def test_modify_board_id_not_found(client):
    create_response = create_board_response(client)
    time_sec = int(time.time())+1
    response = client.patch("/boards/"+str(time_sec), json={
        "name": "board_name_modified",
        "description": "this board description is modified"
    })
    print(response.json())
    assert response.status_code == 404

def test_modify_board_name_already_exist(client):
    create_response1 = create_board_response(client)
    assert create_response1.status_code == 201, create_response1.text
    create_response2 = create_board_response(client, offset=1)
    assert create_response2.status_code == 201, create_response2.text
    response = client.patch("/boards/"+str(create_response1.json()["id"]), json={
        "name": "board_name_modified",
        "description": "this board description is modified"
    })
    response2 = client.patch("/boards/"+str(create_response2.json()["id"]), json={
        "name": "board_name_modified",
        "description": "description is different"
    })
    assert response2.status_code == 400

def test_modify_board_description_empty(client):
    create_response1 = create_board_response(client)
    assert create_response1.status_code == 201, create_response1.text
    response = client.patch("/boards/"+str(create_response1.json()["id"]), json={
        "name": "board_name_modified",
        "description": ""
    })
    assert response.status_code == 200
    assert response.json()["description"] == ""

def test_create_post(client):
    pass
