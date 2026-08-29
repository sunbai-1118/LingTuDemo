import jwt

from app.core.config import settings
from app.services import moderation as mod


class TestRegister:
    def test_register_success(self, client):
        resp = register(client, "xiaoming2024")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert body["data"]["role"] == "USER"
        assert "password" not in body["data"]

    def test_duplicate_username(self, client):
        register(client, "dup_user")
        resp = register(client, "dup_user")
        assert resp.status_code == 409

    def test_empty_username(self, client):
        resp = register(client, "")
        assert resp.status_code == 422

    def test_username_too_long(self, client):
        resp = register(client, "a" * 33)
        assert resp.status_code == 422

    def test_password_too_short(self, client):
        resp = register(client, "shortuser", password="123")
        assert resp.status_code == 422

    def test_password_mismatch(self, client):
        resp = register(client, "mismatchuser", password="pass12345", confirm="pass99999")
        assert resp.status_code == 400
        assert "不一致" in resp.json()["message"]

    def test_moderation_rejected(self, client, fake_moderation):
        fake_moderation.result = fake_moderation.result.__class__(
            allowed=False, category="profanity", reason="包含侮辱性内容"
        )
        resp = register(client, "bad_name")
        assert resp.status_code == 400
        assert "审核" in resp.json()["message"]

    def test_moderation_service_down_fails_closed(self, client, fake_moderation):
        # 真实服务会把任何底层异常包装为 ModerationError（见 test_moderation.py）
        fake_moderation.error = mod.ModerationError("审核服务暂时不可用，请稍后重试")
        resp = register(client, "anyuser01")
        assert resp.status_code == 503
        # 未创建账号
        assert login(client, "anyuser01", "pass12345").status_code == 401


class TestLogin:
    def test_login_success(self, client):
        register(client, "login_user")
        resp = login(client, "login_user", "pass12345")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["token"]
        assert data["user"]["username"] == "login_user"
        assert data["user"]["role"] == "USER"

    def test_wrong_password(self, client):
        register(client, "pwd_user")
        resp = login(client, "pwd_user", "wrongpass99")
        assert resp.status_code == 401

    def test_nonexistent_user(self, client):
        resp = login(client, "no_such_user", "whatever123")
        assert resp.status_code == 401

    def test_token_payload(self, client):
        register(client, "token_user")
        resp = login(client, "token_user", "pass12345")
        payload = jwt.decode(
            resp.json()["data"]["token"],
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        assert payload["role"] == "USER"
        assert payload["sub"]
        assert "exp" in payload


class TestMe:
    def test_me(self, client):
        register(client, "me_user")
        headers = auth_headers(client, "me_user")
        resp = client.get("/api/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["username"] == "me_user"

    def test_me_without_token(self, client):
        assert client.get("/api/auth/me").status_code == 401

    def test_expired_token(self, client, monkeypatch):
        register(client, "expire_user")
        from app.core import security

        monkeypatch.setattr(security.settings, "jwt_expire_minutes", -1)
        headers = auth_headers(client, "expire_user")
        resp = client.get("/api/auth/me", headers=headers)
        assert resp.status_code == 401

    def test_forged_token(self, client):
        forged = jwt.encode({"sub": "1", "role": "ADMIN"}, "wrong-secret", algorithm="HS256")
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged}"})
        assert resp.status_code == 401


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
    return {"Authorization": f"Bearer {resp.json()['data']['token']}"}
