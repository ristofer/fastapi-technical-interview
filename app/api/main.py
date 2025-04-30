from fastapi import Depends, Query
from app.api.deps import encrypt_data, decode_token
from fastapi.routing import APIRouter
from app.api.rate_limit import router as rate_limit_router

router = APIRouter()

# Include the rate limiting router
router.include_router(rate_limit_router, prefix="/rate-limit", tags=["rate-limit"])


@router.get("/user/{user_id}")
async def get_user(user_id: str):
    try:
        numeric_id = int(user_id, base=16) 

        return {
            "user_id": numeric_id,
            "username": f"user_{user_id}",
            "email": f"user_{user_id}@example.com"
        }
    except ValueError:
        return {"error": "Invalid user ID format"}

# State endpoint that returns the user_id from the encrypted token
@router.get("/state")
async def get_state(payload: dict = Depends(decode_token)):
    # Extract user_id from the payload
    user_id = payload.get("user_id")

    # Return the user_id
    return {"user_id": user_id}


# For testing purposes: endpoint to generate a token with user_id=1234
@router.get("/generate-token")
async def generate_token():
    # Create a payload with user_id=1234
    payload = {"user_id": 1234}

    # Encrypt the payload
    token = encrypt_data(payload)

    # Return the token
    return {"token": token}
