from app.models import User


def _login(client, username, password="hunter2"):
    client.post("/api/auth/register", json={"username": username, "password": password})
    client.post("/api/auth/login", json={"username": username, "password": password})


def _promote_to_admin(db_session, username):
    user = db_session.query(User).filter(User.username == username).first()
    user.is_admin = 1
    db_session.commit()


def test_non_admin_cannot_get_settings(client):
    _login(client, "alice")
    resp = client.get("/api/settings")
    assert resp.status_code == 403


def test_settings_requires_authentication(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 401


def test_admin_can_get_and_update_settings(client, db_session):
    _login(client, "admin")
    _promote_to_admin(db_session, "admin")

    resp = client.get("/api/settings")
    assert resp.status_code == 200
    assert resp.json()["auto_backup_enabled"] is True

    resp = client.put("/api/settings", json={"auto_backup_enabled": False})
    assert resp.status_code == 200
    assert resp.json()["auto_backup_enabled"] is False

    resp = client.get("/api/settings")
    assert resp.json()["auto_backup_enabled"] is False
