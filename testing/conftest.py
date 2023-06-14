import os
import sys
from typing import Any, Generator

import pytest
from database.database import get_db
from main import app
from models.models import Base, User
from schemas.schemas import UserCreate
from services.services import create_user, get_password_hash, get_user
from settings import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# this is to include the dir in sys.path so that we can import from session,main.py


# def start_application():
#    app = FastAPI()
#    return app


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# Use connect_args parameter only with sqlite
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)


@pytest.fixture
def client() -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        try:
            db_session = SessionTesting()
            yield db_session
        finally:
            db_session.close

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture
def token_headers(client: TestClient):
    test_username = config.settings.TEST_USERNAME
    test_password = config.settings.TEST_PASS
    db_session = SessionTesting()
    user = get_user(username=test_username, session=db_session)
    if not user:
        user_create = UserCreate(
            username=test_username, password=test_password)
        hashed_password = get_password_hash(user_create.password)
        user = User(username=user_create.username, hashed_password=hashed_password)
        user = create_user(user=user, session=db_session)

    data = {"username": test_username, "password": test_password}

    response = client.post("/login", data=data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
