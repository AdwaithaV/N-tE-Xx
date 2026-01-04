
def test_create_note(client, auth_headers):
    response = client.post(
        "/notes/",
        json={"title": "Test Note", "content": "This is a test note."},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert "id" in data

def test_update_note_creates_version(client, auth_headers):
    # Create
    res = client.post(
        "/notes/",
        json={"title": "Original Title", "content": "Original Content"},
        headers=auth_headers
    )
    note_id = res.json()["id"]

    # Update 1
    client.put(
        f"/notes/{note_id}",
        json={"title": "Updated Title", "content": "Updated Content"},
        headers=auth_headers
    )
    
    # Check History (Expect 1 version: the original state)
    res = client.get(f"/notes/{note_id}/history", headers=auth_headers)
    assert res.status_code == 200
    history = res.json()
    assert len(history) == 1
    assert history[0]["version"] == 1
    assert history[0]["title"] == "Original Title"

    # Update 2
    client.put(
        f"/notes/{note_id}",
        json={"title": "Final Title", "content": "Final Content"},
        headers=auth_headers
    )
    
    # Check History (Expect 2 versions)
    res = client.get(f"/notes/{note_id}/history", headers=auth_headers)
    history = res.json()
    assert len(history) == 2
    # Sort by version desc usually, logic said order_by desc
    assert history[0]["version"] == 2
    assert history[0]["title"] == "Updated Title"

def test_restore_version(client, auth_headers):
    # Create
    res = client.post(
        "/notes/",
        json={"title": "V0 Title", "content": "V0 Content"},
        headers=auth_headers
    )
    note_id = res.json()["id"]
    
    # Update to V1 (History has V0)
    client.put(f"/notes/{note_id}", json={"title": "V1 Title", "content": "V1 Content"}, headers=auth_headers)
    
    # Update to V2 (History has V1, V0)
    client.put(f"/notes/{note_id}", json={"title": "V2 Title", "content": "V2 Content"}, headers=auth_headers)
    
    # Restore Version 1 (which contains "V0 Title")
    # Wait, my logic: 
    # Update 1: history gets version 1 (V0 state). Note is V1 state.
    # Update 2: history gets version 2 (V1 state). Note is V2 state.
    
    # So Version 1 in history is "V0 Title".
    restored = client.post(f"/notes/{note_id}/restore/1", headers=auth_headers)
    assert restored.status_code == 200
    assert restored.json()["title"] == "V0 Title"
    
    # Verify current note is updated
    current = client.get(f"/notes/", headers=auth_headers).json()[0]
    assert current["title"] == "V0 Title"
    
    # Verify a NEW version was created for the state before restore (V2 state)
    history = client.get(f"/notes/{note_id}/history", headers=auth_headers).json()
    # Should have 3 versions now
    assert len(history) == 3
    assert history[0]["version"] == 3
    assert history[0]["title"] == "V2 Title"
