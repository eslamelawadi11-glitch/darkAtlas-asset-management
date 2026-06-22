def test_create_asset(client, headers):
    res = client.post("/assets/", json={
        "type": "domain",
        "value": "example.com",
        "status": "active",
        "source": "scan",
        "tags": ["root"],
        "metadata": {}
    }, headers=headers)
    assert res.status_code == 201
    assert res.json()["value"] == "example.com"


def test_get_asset(client, headers):
    res = client.post("/assets/", json={
        "type": "domain",
        "value": "test-get.com",
        "status": "active",
        "source": "scan",
        "tags": [],
        "metadata": {}
    }, headers=headers)
    asset_id = res.json()["id"]

    res = client.get(f"/assets/{asset_id}")
    assert res.status_code == 200
    assert res.json()["id"] == asset_id


def test_update_asset(client, headers):
    res = client.post("/assets/", json={
        "type": "domain",
        "value": "test-update.com",
        "status": "active",
        "source": "scan",
        "tags": [],
        "metadata": {}
    }, headers=headers)
    asset_id = res.json()["id"]

    res = client.patch(f"/assets/{asset_id}", json={"status": "stale"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "stale"


def test_delete_asset(client, headers):
    res = client.post("/assets/", json={
        "type": "domain",
        "value": "test-delete.com",
        "status": "active",
        "source": "scan",
        "tags": [],
        "metadata": {}
    }, headers=headers)
    asset_id = res.json()["id"]

    res = client.delete(f"/assets/{asset_id}", headers=headers)
    assert res.status_code == 204

    res = client.get(f"/assets/{asset_id}")
    assert res.status_code == 404


def test_list_assets_with_filters(client, headers):
    client.post("/assets/", json={
        "type": "subdomain",
        "value": "api.filter-test.com",
        "status": "active",
        "source": "scan",
        "tags": ["prod"],
        "metadata": {}
    }, headers=headers)

    res = client.get("/assets/?type=subdomain")
    assert res.status_code == 200
    assert res.json()["total"] >= 1


def test_unauthorized_create(client):
    res = client.post("/assets/", json={
        "type": "domain",
        "value": "unauth.com",
        "status": "active",
        "source": "scan",
        "tags": [],
        "metadata": {}
    })
    assert res.status_code == 401