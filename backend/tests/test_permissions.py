from tests.test_auth import auth_headers, login, register


class TestResourceA:
    def test_user_can_access(self, client):
        register(client, "ra_user")
        headers = auth_headers(client, "ra_user")
        resp = client.get("/api/resources/a", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["resource"] == "A"

    def test_admin_can_access(self, client):
        headers = auth_headers(client, "admin", "admin12345")
        assert client.get("/api/resources/a", headers=headers).status_code == 200

    def test_anonymous_gets_401(self, client):
        assert client.get("/api/resources/a").status_code == 401


class TestResourceB:
    def test_user_gets_403(self, client):
        register(client, "rb_user")
        headers = auth_headers(client, "rb_user")
        resp = client.get("/api/resources/b", headers=headers)
        assert resp.status_code == 403
        assert "资源 B" in resp.json()["message"]

    def test_admin_gets_200(self, client):
        headers = auth_headers(client, "admin", "admin12345")
        resp = client.get("/api/resources/b", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["resource"] == "B"

    def test_anonymous_gets_401(self, client):
        assert client.get("/api/resources/b").status_code == 401

    def test_role_in_body_cannot_escalate(self, client):
        """即使伪造 role 也无法提权：身份只来自 JWT。"""
        register(client, "escalate_user")
        headers = auth_headers(client, "escalate_user")
        resp = client.get("/api/resources/b", headers={**headers, "X-Role": "ADMIN"})
        assert resp.status_code == 403
