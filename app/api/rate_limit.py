from fastapi import APIRouter, Query, HTTPException, status
import time
from datetime import datetime
from typing import Dict

router = APIRouter()

# This dictionary will store the request counts for each IP
request_counts: Dict[str, int] = {}
# This dictionary will store the last reset time for each IP
last_reset_times: Dict[str, float] = {}
# Rate limit: 5 requests per minute
RATE_LIMIT = 5
RATE_LIMIT_WINDOW = 60

@router.get("/rate-limited-resource")
async def get_rate_limited_resource(ip: str = Query(..., description="Client IP address")):
    current_time = time.time()
    
    # Initialize request count for this IP if it doesn't exist
    if ip not in request_counts:
        request_counts[ip] = 0
        last_reset_times[ip] = current_time
    
    if current_time > last_reset_times[ip] + RATE_LIMIT_WINDOW:
        last_reset_times[ip] = current_time
    
    # Increment the request count
    request_counts[ip] += 1
    
    # Check if rate limit is exceeded
    if request_counts[ip] > RATE_LIMIT:
        # Return 429 Too Many Requests if rate limit is exceeded
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT} requests per minute."
        )
    
    # If rate limit is not exceeded, return the resource
    return {
        "message": "This is a rate-limited resource",
        "current_count": request_counts[ip],
        "limit": RATE_LIMIT,
        "timestamp": datetime.now().isoformat()
    }
