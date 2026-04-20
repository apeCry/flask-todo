import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, db


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"To Do App" in response.data


def test_add_todo(client):
    response = client.post(
        "/add",
        data={"title": "test task"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"test task" in response.data