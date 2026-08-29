import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app, seed_admin
from app.services import moderation as mod

TEST_DB_URL = "sqlite://"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class FakeModeration:
    """Replace the real LLM call with a configurable stub."""

    def __init__(self):
        self.result = mod.ModerationResult(allowed=True, category="normal", reason="ok")
        self.error: Exception | None = None
        self.calls: list[str] = []

    def __call__(self, username: str) -> mod.ModerationResult:
        self.calls.append(username)
        if self.error is not None:
            raise self.error
        return self.result


@pytest.fixture
def fake_moderation(monkeypatch):
    fake = FakeModeration()
    monkeypatch.setattr("app.api.auth.moderate_username", fake)
    yield fake


@pytest.fixture
def client(fake_moderation):
    Base.metadata.create_all(bind=engine)
    db = TestSession()
    try:
        # 一个默认管理员，供 Resource B 权限测试使用
        from app.core.security import hash_password
        from app.repositories.user_repo import UserRepository

        UserRepository(db).create("admin", hash_password("admin12345"), role="ADMIN")
    finally:
        db.close()

    def override():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    TestSession.close_all()


def register(client, username, password="pass12345", confirm=None):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": password,
            "confirm_password": confirm or password,
        },
    )


def login(client, username, password):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def auth_headers(client, username, password="pass12345"):
    resp = login(client, username, password)
    assert resp.status_code == 200, resp.text
    token = resp.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}
