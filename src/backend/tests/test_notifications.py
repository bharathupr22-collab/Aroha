from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, email: str = "creator@test.com") -> None:
    client.post("/auth/register", json={"name": "Creator", "email": email, "password": "Password123"})
    client.post("/auth/login", json={"email": email, "password": "Password123"})


def test_notifications_lifecycle(client: TestClient):
    _register_and_login(client, "creator_notif@test.com")

    # 1. Trigger media scan
    scan_res = client.post("/notifications/scan")
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["status"] == "completed"
    assert scan_data["new_issues_detected"] > 0

    # 2. Get summary
    sum_res = client.get("/notifications/summary")
    assert sum_res.status_code == 200
    summary = sum_res.json()
    assert summary["total_issues"] > 0
    assert summary["broken_link_issues"] > 0
    assert summary["audio_issues"] > 0
    assert summary["lipsync_issues"] > 0
    assert summary["unresolved_issues"] > 0
    assert summary["unread_count"] > 0

    # 3. List notifications
    notifs_res = client.get("/notifications?status=all")
    assert notifs_res.status_code == 200
    notifs = notifs_res.json()
    assert len(notifs) > 0
    first_issue = notifs[0]
    assert "media" in first_issue
    assert first_issue["media"] is not None
    assert "permalink" in first_issue["media"]
    issue_id = first_issue["id"]

    # 4. Mark read
    read_res = client.put(f"/notifications/{issue_id}/read")
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    # 5. Mark resolved
    resolve_res = client.put(f"/notifications/{issue_id}/resolve")
    assert resolve_res.status_code == 200
    assert resolve_res.json()["is_resolved"] is True
    assert resolve_res.json()["resolved_at"] is not None

    # 6. Check feature catalogs
    for cat in ("broken_link", "audio_loss", "lipsync_mismatch"):
        cat_res = client.get(f"/notifications/catalog/{cat}")
        assert cat_res.status_code == 200
        cat_items = cat_res.json()
        assert len(cat_items) > 0
        for item in cat_items:
            assert item["issue_category"] == cat
            assert item["media"] is not None
