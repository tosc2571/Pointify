def _login(client, username="alice"):
    client.post("/api/auth/register", json={"username": username, "password": "hunter2"})
    client.post("/api/auth/login", json={"username": username, "password": "hunter2"})


def test_create_subtheme(client):
    _login(client)
    theme_id = client.post("/api/themes", json={"title": "Remote work"}).json()["id"]

    resp = client.post(f"/api/themes/{theme_id}/subthemes", json={"title": "Productivity"})
    assert resp.status_code == 201
    assert resp.json()["theme_id"] == theme_id


def test_create_subtheme_requires_authentication(client):
    resp = client.post("/api/themes/1/subthemes", json={"title": "Productivity"})
    assert resp.status_code == 401
