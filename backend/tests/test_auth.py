def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_admin@dharmadiamond.com", "password": "pass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test_admin@dharmadiamond.com"
    assert data["user"]["role"] == "admin"

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_admin@dharmadiamond.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_get_current_user_me(client, admin_headers):
    response = client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test_admin@dharmadiamond.com"

def test_unauthorized_access_fails(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
