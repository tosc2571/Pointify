from app.models import User


def _login(client, username, password="hunter2"):
    client.post("/api/auth/register", json={"username": username, "password": password})
    client.post("/api/auth/login", json={"username": username, "password": password})


def _promote_to_admin(db_session, username):
    user = db_session.query(User).filter(User.username == username).first()
    user.is_admin = 1
    db_session.commit()


def test_non_admin_cannot_list_users(client):
    _login(client, "alice")
    resp = client.get("/api/admin/users")
    assert resp.status_code == 403


def test_admin_can_list_and_create_users(client, db_session):
    _login(client, "admin")
    _promote_to_admin(db_session, "admin")

    resp = client.get("/api/admin/users")
    assert resp.status_code == 200

    resp = client.post("/api/admin/users", json={"username": "newuser", "password": "pw123456"})
    assert resp.status_code == 201


def test_admin_cannot_delete_self(client, db_session):
    _login(client, "admin")
    _promote_to_admin(db_session, "admin")

    admin_id = db_session.query(User).filter(User.username == "admin").first().id

    resp = client.delete(f"/api/admin/users/{admin_id}")
    assert resp.status_code == 400


def test_admin_can_delete_other_user(client, db_session):
    _login(client, "admin")
    _promote_to_admin(db_session, "admin")
    client.post("/api/admin/users", json={"username": "todelete", "password": "pw123456"})

    target_id = db_session.query(User).filter(User.username == "todelete").first().id

    resp = client.delete(f"/api/admin/users/{target_id}")
    assert resp.status_code == 204
