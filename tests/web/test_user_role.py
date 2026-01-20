from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_user_roles():
    response = client.get("/api/user-roles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)