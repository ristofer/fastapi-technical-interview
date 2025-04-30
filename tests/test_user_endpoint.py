from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)


def test_user_endpoint_valid_id():
    """Test that the user endpoint returns correct data for a valid numeric ID"""
    # Make request with a valid numeric ID
    response = client.get("/user/123")

    # Check status code
    assert response.status_code == 200

    # Check response data
    data = response.json()
    assert data["username"] == "user_123"
    assert data["email"] == "user_123@example.com"

def test_user_endpoint_invalid_id():
    """Test that the endpoint correctly handles completely non-numeric IDs"""
    # Make request with random string
    response = client.get("/user/123dedeabali1dfds")
    
    # This should return an error
    assert response.status_code == 400

def test_user_endpoint_invalid_id_type():
    """Test that the endpoint correctly handles non-numeric IDs"""
    response = client.get("/user/abc")

    # This should return an error
    assert response.status_code == 400
