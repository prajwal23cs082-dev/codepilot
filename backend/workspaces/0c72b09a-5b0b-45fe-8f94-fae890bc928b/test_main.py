from fastapi.testclient import TestClient
from app.main import app, users_db

client = TestClient(app)

def setup_function():
    users_db.clear()
    global user_id_counter
    import app.main
    app.main.user_id_counter = 1

def test_create_user():
    response = client.post(
        "/users",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["id"] == 1

def test_get_users():
    client.post(
        "/users",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "testuser"

# This test will fail until JWT is implemented correctly and the endpoint is protected
def test_unauthenticated_users_forbidden():
    response = client.get("/users")
    # This should be 401 if JWT is required
    # Intentional failure for demo:
    assert response.status_code == 401
