def test_register_and_login(client):
    resp = client.post("/api/auth/register", json={"username": "alice", "password": "hunter2"})
    assert resp.status_code == 201
    assert resp.json()["username"] == "alice"

    resp = client.post("/api/auth/login", json={"username": "alice", "password": "hunter2"})
    assert resp.status_code == 200

    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"


def test_login_with_wrong_password_fails(client):
    client.post("/api/auth/register", json={"username": "bob", "password": "correct-horse"})
    resp = client.post("/api/auth/login", json={"username": "bob", "password": "wrong"})
    assert resp.status_code == 401


def test_register_duplicate_username_fails(client):
    client.post("/api/auth/register", json={"username": "carol", "password": "pw12345"})
    resp = client.post("/api/auth/register", json={"username": "carol", "password": "pw12345"})
    assert resp.status_code == 400


def test_me_requires_authentication(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_logout_clears_session(client):
    client.post("/api/auth/register", json={"username": "dave", "password": "pw12345"})
    client.post("/api/auth/login", json={"username": "dave", "password": "pw12345"})
    resp = client.post("/api/auth/logout")
    assert resp.status_code == 200
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
