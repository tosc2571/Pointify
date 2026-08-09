def _login(client, username="alice"):
    client.post("/api/auth/register", json={"username": username, "password": "hunter2"})
    client.post("/api/auth/login", json={"username": username, "password": "hunter2"})


def _make_subtheme(client):
    theme_id = client.post("/api/themes", json={"title": "Remote work"}).json()["id"]
    return client.post(f"/api/themes/{theme_id}/subthemes", json={"title": "Productivity"}).json()["id"]


def test_create_point(client):
    _login(client)
    subtheme_id = _make_subtheme(client)

    resp = client.post(
        f"/api/subthemes/{subtheme_id}/points",
        json={"type": "pro", "text": "Fewer distractions", "rating": 5},
    )
    assert resp.status_code == 201
    assert resp.json()["rating"] == 5


def test_create_point_for_unknown_subtheme_returns_404(client):
    _login(client)
    resp = client.post("/api/subthemes/999/points", json={"type": "pro", "text": "x", "rating": 3})
    assert resp.status_code == 404


def test_create_point_requires_authentication(client):
    resp = client.post("/api/subthemes/1/points", json={"type": "pro", "text": "x", "rating": 3})
    assert resp.status_code == 401
