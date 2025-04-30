from fastapi.testclient import TestClient
from dotenv import load_dotenv
import json
from app.core.data_anonymizer import DataAnonymizer
from app.main import app
from app.api.deps import encrypt_data, decrypt_data

# Load environment variables
load_dotenv()

# Create test client
client = TestClient(app)


def test_encrypt_decrypt():
    """Test that our custom encryption/decryption functions work correctly"""
    # Create a payload
    payload = {"user_id": 1234}
    key = bytes.fromhex(
        "cb88f6566bc2ec17a878814a0127463ba685860d66ba0135d615b46a2dc51e69"
    )
    # Encrypt the payload
    token = encrypt_data(payload, key=key)

    # Decrypt the token
    decrypted_payload = decrypt_data(token, key=key)

    # Check that the decrypted payload matches the original
    assert decrypted_payload == payload


def test_generate_token():
    """Test that the generate-token endpoint returns a valid encrypted token with user_id=1234"""
    # Make request to generate token
    response = client.get("/generate-token")

    # Check status code
    assert response.status_code == 200

    # Check that token is in response
    assert "token" in response.json()

    # Get token from response
    payload = response.json()["token"]

    # Check that user_id is in payload and equals 1234
    assert "user_id" in payload
    assert payload["user_id"] == 1234


def test_state_endpoint():
    """Test that the state endpoint returns the user_id from the encrypted token"""
    # Generate a token with user_id=1234
    payload = {"user_id": 1234}
    anonymizer = DataAnonymizer(
        "cb88f6566bc2ec17a878814a0127463ba685860d66ba0135d615b46a2dc51e69"
    )
    key = bytes.fromhex(
        "cb88f6566bc2ec17a878814a0127463ba685860d66ba0135d615b46a2dc51e69"
    )
    token = anonymizer.encrypt(json.dumps(payload), key)

    # Make request to state endpoint with token
    response = client.get("/state", headers={"Authorization": f"{token}"})

    # Check status code
    assert response.status_code == 200

    # Check response
    assert response.json() == {"user_id": 1234}


def test_state_endpoint_invalid_token():
    """Test that the state endpoint returns 401 for invalid token"""
    # Make request to state endpoint with invalid token
    response = client.get("/state", headers={"Authorization": "Bearer invalid_token"})

    # Check status code
    assert response.status_code == 401
