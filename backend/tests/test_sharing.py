def _login(client, username, password="hunter2"):
    client.post("/api/auth/register", json={"username": username, "password": password})
    client.post("/api/auth/login", json={"username": username, "password": password})


def _logout(client):
    client.post("/api/auth/logout")


def _register_only(client, username, password="hunter2"):
    client.post("/api/auth/register", json={"username": username, "password": password})


def test_owner_can_see_own_theme(client):
    _login(client, "alice")
    theme_id = client.post("/api/themes", json={"title": "Alice's theme"}).json()["id"]

    resp = client.get(f"/api/themes/{theme_id}")
    assert resp.status_code == 200
    assert resp.json()["owner_id"] is not None


def test_other_user_cannot_see_unshared_theme(client):
    _login(client, "alice")
    theme_id = client.post("/api/themes", json={"title": "Alice's theme"}).json()["id"]
    _logout(client)

    _login(client, "bob")
    resp = client.get(f"/api/themes/{theme_id}")
    assert resp.status_code == 404

    resp = client.get("/api/themes")
    assert resp.json() == []


def test_theme_list_only_shows_own_and_shared_themes(client):
    _login(client, "alice")
    client.post("/api/themes", json={"title": "Alice's theme"})
    _logout(client)

    _login(client, "bob")
    client.post("/api/themes", json={"title": "Bob's theme"})

    resp = client.get("/api/themes")
    titles = [t["title"] for t in resp.json()]
    assert titles == ["Bob's theme"]


def test_owner_can_share_theme_and_shared_user_gains_access(client):
    _register_only(client, "bob")
    _login(client, "alice")
    theme_id = client.post("/api/themes", json={"title": "Alice's theme"}).json()["id"]
    resp = client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"})
    assert resp.status_code == 201
    _logout(client)

    _login(client, "bob")
    resp = client.get(f"/api/themes/{theme_id}")
    assert resp.status_code == 200

    resp = client.get("/api/themes")
    assert [t["id"] for t in resp.json()] == [theme_id]


def test_shared_user_can_add_subtheme_and_point(client):
    _register_only(client, "bob")
    _login(client, "alice")
    theme_id = client.post("/api/themes", json={"title": "Alice's theme"}).json()["id"]
    client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"})
    _logout(client)

    _login(client, "bob")
    resp = client.post(f"/api/themes/{theme_id}/subthemes", json={"title": "Bob's subtheme"})
    assert resp.status_code == 201
    subtheme_id = resp.json()["id"]

    resp = client.post(
        f"/api/subthemes/{subtheme_id}/points",
        json={"type": "pro", "text": "Bob's point", "rating": 4},
    )
    assert resp.status_code == 201


def test_non_owner_cannot_share_theme(client):
    _register_only(client, "bob")
    _register_only(client, "carol")
    _login(client, "alice")
    theme_id = client.post("/api/themes", json={"title": "Alice's theme"}).json()["id"]
    client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"})
    _logout(client)

    _login(client, "bob")
    resp = client.post(f"/api/themes/{theme_id}/shares", json={"username": "carol"})
    assert resp.status_code == 403


def test_share_with_unknown_username_returns_404(client):
    _login(client, "alice")
    theme_id = client.post("/api/themes", json={"title": "Alice's theme"}).json()["id"]

    resp = client.post(f"/api/themes/{theme_id}/shares", json={"username": "nobody"})
    assert resp.status_code == 404


def test_duplicate_share_returns_400(client):
    _login(client, "alice")
    theme_id = client.post("/api/themes", json={"title": "Alice's theme"}).json()["id"]
    client.post("/api/auth/logout")
    _login(client, "bob")
    _logout(client)
    _login(client, "alice")

    client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"})
    resp = client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"})
    assert resp.status_code == 400


def test_owner_can_list_and_revoke_share(client):
    _login(client, "alice")
    theme_id = client.post("/api/themes", json={"title": "Alice's theme"}).json()["id"]
    client.post("/api/auth/logout")
    _login(client, "bob")
    _logout(client)
    _login(client, "alice")

    share = client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"}).json()

    resp = client.get(f"/api/themes/{theme_id}/shares")
    assert resp.status_code == 200
    assert [s["username"] for s in resp.json()] == ["bob"]

    resp = client.delete(f"/api/themes/{theme_id}/shares/{share['user_id']}")
    assert resp.status_code == 204

    _logout(client)
    _login(client, "bob")
    resp = client.get(f"/api/themes/{theme_id}")
    assert resp.status_code == 404
