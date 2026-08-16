def _login(client, username="alice"):
    client.post("/api/auth/register", json={"username": username, "password": "hunter2"})
    client.post("/api/auth/login", json={"username": username, "password": "hunter2"})


def test_create_and_list_themes(client):
    _login(client)
    resp = client.post("/api/themes", json={"title": "Remote work"})
    assert resp.status_code == 201
    theme_id = resp.json()["id"]

    resp = client.get("/api/themes")
    assert resp.status_code == 200
    assert any(t["id"] == theme_id for t in resp.json())


def test_theme_requires_authentication(client):
    resp = client.get("/api/themes")
    assert resp.status_code == 401


def test_theme_detail_includes_stats(client):
    _login(client)
    theme_id = client.post("/api/themes", json={"title": "Coffee vs tea"}).json()["id"]
    subtheme_id = client.post(f"/api/themes/{theme_id}/subthemes", json={"title": "Health"}).json()["id"]
    client.post(
        f"/api/subthemes/{subtheme_id}/points",
        json={"type": "pro", "text": "Antioxidants", "rating": 4},
    )
    client.post(
        f"/api/subthemes/{subtheme_id}/points",
        json={"type": "contra", "text": "Caffeine", "rating": 2},
    )

    resp = client.get(f"/api/themes/{theme_id}")
    assert resp.status_code == 200
    stats = resp.json()["stats"]
    assert stats["total_points"] == 2
    assert stats["pro_count"] == 1
    assert stats["contra_count"] == 1
    assert stats["avg_rating"] == 3.0


def test_get_unknown_theme_returns_404(client):
    _login(client)
    resp = client.get("/api/themes/999")
    assert resp.status_code == 404


def test_theme_detail_includes_subthemes_with_points(client):
    _login(client)
    theme_id = client.post("/api/themes", json={"title": "Coffee vs tea"}).json()["id"]
    subtheme_id = client.post(f"/api/themes/{theme_id}/subthemes", json={"title": "Health"}).json()["id"]
    client.post(
        f"/api/subthemes/{subtheme_id}/points",
        json={"type": "pro", "text": "Antioxidants", "rating": 4},
    )

    resp = client.get(f"/api/themes/{theme_id}")
    assert resp.status_code == 200
    subthemes = resp.json()["subthemes"]
    assert len(subthemes) == 1
    assert subthemes[0]["title"] == "Health"
    assert len(subthemes[0]["points"]) == 1
    assert subthemes[0]["points"][0]["text"] == "Antioxidants"


def test_export_markdown_includes_title_stats_and_points(client):
    _login(client)
    theme_id = client.post("/api/themes", json={"title": "Coffee vs tea"}).json()["id"]
    subtheme_id = client.post(f"/api/themes/{theme_id}/subthemes", json={"title": "Health"}).json()["id"]
    client.post(
        f"/api/subthemes/{subtheme_id}/points",
        json={"type": "pro", "text": "Antioxidants", "rating": 4},
    )
    client.post(f"/api/themes/{theme_id}/subthemes", json={"title": "Empty subtheme"})

    resp = client.get(f"/api/themes/{theme_id}/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/markdown")

    body = resp.text
    assert "# Coffee vs tea" in body
    assert "1 points" in body
    assert "## Health" in body
    assert "**Pro** (★4): Antioxidants" in body
    assert "## Empty subtheme" in body
    assert "_No points yet._" in body


def test_export_markdown_requires_theme_access(client):
    _login(client, "alice")
    theme_id = client.post("/api/themes", json={"title": "Alice's theme"}).json()["id"]
    client.post("/api/auth/logout")

    _login(client, "bob")
    resp = client.get(f"/api/themes/{theme_id}/export")
    assert resp.status_code == 404
