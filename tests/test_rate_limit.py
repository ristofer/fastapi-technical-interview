from fastapi.testclient import TestClient
from app.main import app
import time

# Create test client
client = TestClient(app)


def test_rate_limit_single_request():
    """Test that a single request to the rate-limited endpoint works correctly"""
    # Make a single request to the rate-limited endpoint
    response = client.get("/rate-limit/rate-limited-resource?ip=127.0.0.1")
    
    # Check status code
    assert response.status_code == 200
    
    # Check response data
    data = response.json()
    assert data["message"] == "This is a rate-limited resource"
    assert data["current_count"] == 1
    assert data["limit"] == 5


def test_rate_limit_multiple_requests_within_limit():
    """Test that multiple requests within the rate limit work correctly"""
    # Make 5 requests (which is the limit)
    for i in range(5):
        response = client.get("/rate-limit/rate-limited-resource?ip=192.168.1.1")
        
        # All requests should succeed
        assert response.status_code == 200
        
        # Check the count increases
        data = response.json()
        assert data["current_count"] == i + 1


def test_rate_limit_exceeded():
    """Test that exceeding the rate limit returns a 429 status code"""
    # Make 6 requests (one more than the limit)
    for i in range(6):
        response = client.get("/rate-limit/rate-limited-resource?ip=10.0.0.1")
        
        if i < 5:
            # First 5 requests should succeed
            assert response.status_code == 200
        else:
            # 6th request should fail with 429 Too Many Requests
            assert response.status_code == 429
            assert "Rate limit exceeded" in response.json()["detail"]


def test_rate_limit_bug_after_window():
    """
    Test that demonstrates the rate limiting bug.
    
    The bug is that the rate limit counter doesn't reset properly after the time window,
    causing the endpoint to incorrectly block legitimate requests.
    
    This test will:
    1. Make 5 requests (reaching the limit)
    2. Wait for the rate limit window to pass
    3. Make another request, which should succeed if the counter resets properly
       but will fail due to the bug
    """
    # IP address for this test
    test_ip = "172.16.0.1"
    
    # Make 5 requests (reaching the limit)
    for i in range(5):
        response = client.get(f"/rate-limit/rate-limited-resource?ip={test_ip}")
        assert response.status_code == 200
    
    # Wait for the rate limit window to pass
    # Note: In a real test, you might mock the time instead of actually waiting
    # time.sleep(61)  # Wait just over the 60-second window
    
    # For the purpose of this test, we'll simulate the time passing by directly
    # modifying the last_reset_times dictionary in the rate_limit module
    # This is just for demonstration - in a real test, you'd use proper mocking
    from app.api.rate_limit import last_reset_times
    if test_ip in last_reset_times:
        # Set the last reset time to be more than the window in the past
        last_reset_times[test_ip] = time.time() - 61
    
    # Make another request after the window
    response = client.get(f"/rate-limit/rate-limited-resource?ip={test_ip}")
    

    assert response.status_code == 200
