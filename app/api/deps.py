from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import os
import json

from app.core.data_anonymizer import DataAnonymizer

# Load environment variables
load_dotenv()
security = HTTPBearer()


# Encrypt data
def encrypt_data(data: dict, key: bytes = None) -> str:
    # Secret key for encryption
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_super_secret_key_here")
    # Ensure the key is 32 bytes for AES-256

    # Create DataAnonymizer instance
    anonymizer = DataAnonymizer(SECRET_KEY)
    # Convert data to JSON string
    json_data = json.dumps(data)

    # Encrypt the data using DataAnonymizer
    return anonymizer.encrypt(json_data, key=anonymizer.key)


# Decrypt data
def decrypt_data(token: str, key: bytes | None = None) -> dict:
    # Secret key for encryption
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_super_secret_key_here")
    # Ensure the key is 32 bytes for AES-256

    # Create DataAnonymizer instance
    anonymizer = DataAnonymizer(SECRET_KEY)
    try:
        # Decrypt the data using DataAnonymizer
        json_data = anonymizer.decrypt(token, key=anonymizer.key)

        # Parse JSON data
        return json.loads(json_data)
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Function to decode token
def decode_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Get the token from the Authorization header
        token = credentials.credentials

        # Decrypt the token
        payload = decrypt_data(token)

        # Return the decrypted payload
        return payload
    except Exception as e:
        # If token is invalid, raise an exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
