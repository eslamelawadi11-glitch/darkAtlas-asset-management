def test_bulk_import_no_duplicates(client, headers):
    payload = {
        "assets": [
            {"type": "domain", "value": "dedup.com", "source": "import", "tags": ["a"], "metadata": {}},
            {"type": "domain", "value": "dedup.com", "source": "import", "tags": ["b"], "metadata": {}},
        ]
    }
    res = client.post("/assets/bulk-import", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["created"] == 1
    assert data["updated"] == 1


def test_bulk_import_merges_tags(client, headers):
    payload = {
        "assets": [
            {"type": "domain", "value": "merge-tags.com", "source": "import", "tags": ["x"], "metadata": {}},
            {"type": "domain", "value": "merge-tags.com", "source": "import", "tags": ["y"], "metadata": {}},
        ]
    }
    client.post("/assets/bulk-import", json=payload, headers=headers)

    res = client.get("/assets/?value_contains=merge-tags.com")
    asset = res.json()["items"][0]
    assert "x" in asset["tags"]
    assert "y" in asset["tags"]


def test_stale_asset_reactivated(client, headers):
    res = client.post("/assets/", json={
        "type": "domain",
        "value": "stale-test.com",
        "status": "active",
        "source": "scan",
        "tags": [],
        "metadata": {}
    }, headers=headers)
    asset_id = res.json()["id"]

    client.patch(f"/assets/{asset_id}/stale", headers=headers)

    payload = {
        "assets": [
            {"type": "domain", "value": "stale-test.com", "source": "import", "tags": [], "metadata": {}}
        ]
    }
    client.post("/assets/bulk-import", json=payload, headers=headers)

    res = client.get(f"/assets/{asset_id}")
    assert res.json()["status"] == "active"