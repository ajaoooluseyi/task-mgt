
def test_create_user(client):
    data = {
        "username": "testinguser",
        "password": "testing",
    }
    response = client.post("/signup/", json=data)
    assert response.status_code == 201
    new_data = response.json()
    assert new_data["username"] == "testinguser"
    assert new_data["is_active"] == True
