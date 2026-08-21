def _login(client, username, password="hunter2"):
    client.post("/api/auth/register", json={"username": username, "password": password})
    client.post("/api/auth/login", json={"username": username, "password": password})


def _logout(client):
    client.post("/api/auth/logout")


def _register_only(client, username, password="hunter2"):
    client.post("/api/auth/register", json={"username": username, "password": password})


def _make_theme_with_subtheme_and_point(client):
    theme_id = client.post("/api/themes", json={"title": "Coffee vs tea"}).json()["id"]
    subtheme_id = client.post(f"/api/themes/{theme_id}/subthemes", json={"title": "Health"}).json()["id"]
    point_id = client.post(
        f"/api/subthemes/{subtheme_id}/points",
        json={"type": "pro", "text": "Antioxidants", "rating": 4},
    ).json()["id"]
    return theme_id, subtheme_id, point_id


# --- theme ---


def test_owner_can_rename_theme(client):
    _login(client, "alice")
    theme_id, _, _ = _make_theme_with_subtheme_and_point(client)

    resp = client.patch(f"/api/themes/{theme_id}", json={"title": "Coffee vs tea (revised)"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Coffee vs tea (revised)"


def test_shared_user_can_rename_theme(client):
    _register_only(client, "bob")
    _login(client, "alice")
    theme_id, _, _ = _make_theme_with_subtheme_and_point(client)
    client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"})
    _logout(client)

    _login(client, "bob")
    resp = client.patch(f"/api/themes/{theme_id}", json={"title": "Renamed by bob"})
    assert resp.status_code == 200


def test_user_without_access_cannot_rename_theme(client):
    _login(client, "alice")
    theme_id, _, _ = _make_theme_with_subtheme_and_point(client)
    _logout(client)

    _login(client, "bob")
    resp = client.patch(f"/api/themes/{theme_id}", json={"title": "Hijacked"})
    assert resp.status_code == 404


def test_shared_user_cannot_delete_theme(client):
    _register_only(client, "bob")
    _login(client, "alice")
    theme_id, _, _ = _make_theme_with_subtheme_and_point(client)
    client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"})
    _logout(client)

    _login(client, "bob")
    resp = client.delete(f"/api/themes/{theme_id}")
    assert resp.status_code == 403


def test_owner_can_delete_theme_and_it_cascades(client):
    _login(client, "alice")
    theme_id, subtheme_id, point_id = _make_theme_with_subtheme_and_point(client)

    resp = client.delete(f"/api/themes/{theme_id}")
    assert resp.status_code == 204

    assert client.get(f"/api/themes/{theme_id}").status_code == 404
    # The subtheme/point are gone too — re-creating a point against the deleted subtheme
    # id must fail since it no longer exists.
    resp = client.post(
        f"/api/subthemes/{subtheme_id}/points",
        json={"type": "pro", "text": "x", "rating": 3},
    )
    assert resp.status_code == 404


# --- subtheme ---


def test_owner_can_rename_and_delete_subtheme(client):
    _login(client, "alice")
    theme_id, subtheme_id, _ = _make_theme_with_subtheme_and_point(client)

    resp = client.patch(f"/api/themes/{theme_id}/subthemes/{subtheme_id}", json={"title": "Wellbeing"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Wellbeing"

    resp = client.delete(f"/api/themes/{theme_id}/subthemes/{subtheme_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/themes/{theme_id}")
    assert resp.json()["subthemes"] == []


def test_shared_user_can_rename_and_delete_subtheme(client):
    _register_only(client, "bob")
    _login(client, "alice")
    theme_id, subtheme_id, _ = _make_theme_with_subtheme_and_point(client)
    client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"})
    _logout(client)

    _login(client, "bob")
    resp = client.patch(f"/api/themes/{theme_id}/subthemes/{subtheme_id}", json={"title": "Renamed"})
    assert resp.status_code == 200

    resp = client.delete(f"/api/themes/{theme_id}/subthemes/{subtheme_id}")
    assert resp.status_code == 204


def test_user_without_access_cannot_touch_subtheme(client):
    _login(client, "alice")
    theme_id, subtheme_id, _ = _make_theme_with_subtheme_and_point(client)
    _logout(client)

    _login(client, "bob")
    resp = client.patch(f"/api/themes/{theme_id}/subthemes/{subtheme_id}", json={"title": "Hijacked"})
    assert resp.status_code == 404
    resp = client.delete(f"/api/themes/{theme_id}/subthemes/{subtheme_id}")
    assert resp.status_code == 404


# --- point ---


def test_owner_can_edit_and_delete_point(client):
    _login(client, "alice")
    _, subtheme_id, point_id = _make_theme_with_subtheme_and_point(client)

    resp = client.patch(
        f"/api/subthemes/{subtheme_id}/points/{point_id}",
        json={"type": "contra", "text": "Actually jittery", "rating": 2},
    )
    assert resp.status_code == 200
    assert resp.json()["type"] == "contra"
    assert resp.json()["text"] == "Actually jittery"

    resp = client.delete(f"/api/subthemes/{subtheme_id}/points/{point_id}")
    assert resp.status_code == 204


def test_shared_user_can_edit_and_delete_another_users_point(client):
    _register_only(client, "bob")
    _login(client, "alice")
    theme_id, subtheme_id, point_id = _make_theme_with_subtheme_and_point(client)
    client.post(f"/api/themes/{theme_id}/shares", json={"username": "bob"})
    _logout(client)

    # bob (not the point's author) edits and deletes alice's point.
    _login(client, "bob")
    resp = client.patch(
        f"/api/subthemes/{subtheme_id}/points/{point_id}",
        json={"type": "pro", "text": "Edited by bob", "rating": 5},
    )
    assert resp.status_code == 200

    resp = client.delete(f"/api/subthemes/{subtheme_id}/points/{point_id}")
    assert resp.status_code == 204


def test_user_without_access_cannot_touch_point(client):
    _login(client, "alice")
    _, subtheme_id, point_id = _make_theme_with_subtheme_and_point(client)
    _logout(client)

    _login(client, "bob")
    resp = client.patch(
        f"/api/subthemes/{subtheme_id}/points/{point_id}",
        json={"type": "pro", "text": "Hijacked", "rating": 1},
    )
    assert resp.status_code == 404
    resp = client.delete(f"/api/subthemes/{subtheme_id}/points/{point_id}")
    assert resp.status_code == 404
