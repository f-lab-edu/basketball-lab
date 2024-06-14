from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time, uuid
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

def create_board_response(client):
    id = uuid.uuid1()
    response = client.post("/boards/", json={
        "name": "board"+str(int(id)),
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

def test_retrieve_board_id_not_exist(client, clear_database):
    response = client.get("/boards/1")
    assert response.status_code == 404

def test_retrieve_all_boards(client):
    create_board_response(client)
    response = client.get("/boards/")
    assert response.status_code == 200

def test_retrieve_all_boards_not_exist(client, clear_database):
    response = client.get("/boards")
    assert response.status_code == 404

def test_modify_board(client):
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
    assert response.status_code == 404

def test_modify_board_name_already_exist(client):
    create_response1 = create_board_response(client)
    assert create_response1.status_code == 201, create_response1.text    
    create_response2 = create_board_response(client)
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

def test_delete_board(client):
    create_response = create_board_response(client)
    response = client.delete("/boards/"+str(create_response.json()["id"]))
    assert response.status_code == 204

def test_delete_board_id_not_found(client):
    time_sec = int(time.time())
    response = client.delete("/boards/"+str(time_sec))
    assert response.status_code == 404
    
def test_create_post(client):
    board_response = create_board_response(client)
    assert board_response.status_code == 201
    board_id = int(board_response.json()["id"])

    post_data = {
        "title": "Hello World",
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
                    Maecenas sodales, odio et accumsan auctor, purus erat aliquam mauris, \
                    et maximus quam libero ut nulla. ",
        "author": "author1"
    }
    
    response = client.post(f"/boards/{board_id}/posts", json=post_data)
    assert response.status_code == 201
    assert response.json()["title"] == post_data["title"]
    assert response.json()["content"] == post_data["content"]
    assert response.json()["author"] == post_data["author"]

def create_post_response(client, boardId: int):
    post_data = {
        "title": "Hello World",
        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
                    Maecenas sodales, odio et accumsan auctor, purus erat aliquam mauris, \
                    et maximus quam libero ut nulla.",
        "author": "author1"
    }

    response = client.post("/boards/"+str(boardId)+"/posts", json=post_data)
    return response

def create_post_by_data(client, board_id, title, content, author):
    post_data = {
        "title": title,
        "content": content,
        "author": author
    }
    response = client.post(f"/boards/{board_id}/posts", json=post_data)
    return response

def test_create_post_board_id_not_found(client, clear_database):
    post_response = create_post_response(client, 1)
    assert post_response.status_code == 404

def test_retrieve_post(client, clear_database):
    board_response = create_board_response(client)
    board_id = board_response.json()["id"]
    post_response = create_post_response(client, board_id)
    post_id = post_response.json()["id"]
    response = client.get("/boards/"+str(board_id)+"/posts/"+str(post_id))
    assert response.status_code == 200
    assert response.json()["title"] == "Hello World"
    assert response.json()["author"] == "author1"

def test_retrieve_post_board_id_not_found(client, clear_database):
    board_id, post_id = 1,1
    response = client.get("/boards/"+str(board_id)+"/posts/"+str(post_id))
    assert response.status_code == 404
    assert response.json()["detail"] == "Board with this ID does not exist"

def test_retrieve_post_post_id_not_found(client, clear_database):
    board_response = create_board_response(client)
    board_id, post_id = board_response.json()["id"], 1
    response = client.get("/boards/"+str(board_id)+"/posts/"+str(post_id))
    assert response.status_code == 404
    assert response.json()["detail"] == "Post with this ID does not exist"

def test_retrieve_all_posts_count_twenty(client, clear_database):
    board_response = create_board_response(client)
    board_id = board_response.json()['id']

    for i in range(20):
        title = f"Post {i+1}"
        content = f"Content of post {i + 1}"
        author = f"author {i + 1}"
        create_post_by_data(client, board_id, title, content, author)
   
    response = client.get(f"/boards/{board_id}/posts/", params={"offset": 0, "limit": 20})
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 20, "Number of posts retrieved does not match the number created"

    for i, post in enumerate(posts):
        assert post['title'] == f"Post {i + 1}", f"Title mismatch for post {i + 1}"
        assert post['content'] == f"Content of post {i + 1}", f"Content mismatch for post {i + 1}"
        assert post['author'] == f"author {i + 1}", f"Author mismatch for post {i + 1}"

def test_retrieve_all_posts_exceeding_twenty(client, clear_database):
    board_response = create_board_response(client)
    board_id = board_response.json()['id']

    for i in range(20):
        title = f"Post {i+1}"
        content = f"Content of post {i + 1}"
        author = f"author {i + 1}"
        create_post_by_data(client, board_id, title, content, author)
   
    response = client.get(f"/boards/{board_id}/posts/", params={"offset": 5, "limit": 27})
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 17, "Number of posts retrieved does not match the number created"

    for i, post in enumerate(posts,5):
        assert post['title'] == f"Post {i + 1}", f"Title mismatch for post {i + 1}"
        assert post['content'] == f"Content of post {i + 1}", f"Content mismatch for post {i + 1}"
        assert post['author'] == f"author {i + 1}", f"Author mismatch for post {i + 1}"

def test_retrieve_posts_board_id_not_found(client, clear_database):
    boardId = 1
    response = client.get(f"/boards/{boardId}/posts/", params={"offset": 0, "limit": 20})
    assert response.status_code == 404
    assert response.json()["detail"] == "Board with this ID does not exist"

def test_retrieve_posts_post_id_not_found(client, clear_database):
    board_response = create_board_response(client)
    board_id = board_response.json()["id"]
    response = client.get(f"/boards/{board_id}/posts/", params={"offset": 0, "limit": 20})
    assert response.status_code == 404
    assert response.json()["detail"] == "No posts found"
