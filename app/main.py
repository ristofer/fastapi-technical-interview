from fastapi import FastAPI
from app.api.main import router as api_router


# Initialize FastAPI app
app = FastAPI(title="Custom Encryption API")

app.include_router(api_router, tags=["api"])
