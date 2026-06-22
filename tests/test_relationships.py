def create_asset(client, headers, value, type="domain"):
    res = client.post("/assets/", json={
        "type": type,
        "value": value,
        "status": "active",
        "source": "scan",
        "tags": [],
        "metadata": {}
    }, headers=headers)
    return res.json()["id"]


def test_create_relationship(client, headers):
    source_id = create_asset(client, headers, "rel-source.com")
    target_id = create_asset(client, headers, "rel-target.com")

    res = client.post("/relationships/", json={
        "source_id": source_id,
        "target_id": target_id,
        "relation_type": "subdomain_of"
    }, headers=headers)
    assert res.status_code == 201
    assert res.json()["relation_type"] == "subdomain_of"


def test_no_duplicate_relationship(client, headers):
    source_id = create_asset(client, headers, "dup-source.com")
    target_id = create_asset(client, headers, "dup-target.com")

    payload = {
        "source_id": source_id,
        "target_id": target_id,
        "relation_type": "resolves_to"
    }
    client.post("/relationships/", json=payload, headers=headers)
    res = client.post("/relationships/", json=payload, headers=headers)
    assert res.status_code == 409


def test_get_asset_graph(client, headers):
    source_id = create_asset(client, headers, "graph-source.com")
    target_id = create_asset(client, headers, "graph-target.com")

    client.post("/relationships/", json={
        "source_id": source_id,
        "target_id": target_id,
        "relation_type": "subdomain_of"
    }, headers=headers)

    res = client.get(f"/relationships/graph/{source_id}")
    assert res.status_code == 200
    assert len(res.json()["outgoing"]) >= 1