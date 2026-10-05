"""
Integration tests for API endpoints

Tests include:
- Health check endpoint
- User registration and login
- Model status endpoint
- Detection history endpoint
- Authentication flow
"""
import pytest
import time
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app"""
    try:
        from app.main import app
        return TestClient(app)
    except ImportError as e:
        pytest.skip(f"Cannot import app: {e}")


@pytest.fixture(scope="module")
def test_user_credentials():
    """Create unique test user credentials"""
    timestamp = int(time.time())
    return {
        "username": f"test_user_{timestamp}",
        "password": "Test123456",  # Updated to meet password policy: uppercase, lowercase, digit
        "email": f"test_user_{timestamp}@test.com"
    }


@pytest.fixture(scope="module")
def auth_token(client, test_user_credentials):
    """Register a test user and return auth token"""
    # Register user
    response = client.post("/register", json=test_user_credentials)
    
    # If user already exists, that's okay
    if response.status_code not in [200, 400]:
        pytest.fail(f"Registration failed: {response.text}")
    
    # Login to get token
    login_data = {
        "username": test_user_credentials["username"],
        "password": test_user_credentials["password"]
    }
    response = client.post("/token", data=login_data)
    
    if response.status_code != 200:
        pytest.fail(f"Login failed: {response.text}")
    
    token_data = response.json()
    return token_data["access_token"]


@pytest.mark.integration
def test_health_endpoint(client):
    """Test that health endpoint returns 200"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


@pytest.mark.integration
def test_register_user(client, test_user_credentials):
    """Test user registration endpoint"""
    # Use a different username to avoid conflicts
    unique_creds = test_user_credentials.copy()
    unique_creds["username"] = f"{unique_creds['username']}_reg"
    unique_creds["email"] = f"{unique_creds['username']}@test.com"
    
    response = client.post("/register", json=unique_creds)
    
    # Either success (200) or user exists (400) is acceptable
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.json()
        # API returns {"success": True, "user": {...}}
        assert "success" in data or "user" in data


@pytest.mark.integration
def test_login_success(client, test_user_credentials):
    """Test successful login"""
    # First register
    client.post("/register", json=test_user_credentials)
    
    # Then login
    login_data = {
        "username": test_user_credentials["username"],
        "password": test_user_credentials["password"]
    }
    response = client.post("/token", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.integration
def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistent_user_xyz",
        "password": "wrongpassword"
    }
    response = client.post("/token", data=login_data)
    
    assert response.status_code == 401


@pytest.mark.integration
def test_model_status_authenticated(client, auth_token):
    """Test model status endpoint with authentication"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/models/status", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "trufor" in data
    assert "deepfakebench" in data
    
    # Check TruFor status
    assert "available" in data["trufor"]
    assert "path" in data["trufor"]
    
    # Check DeepfakeBench status
    assert "available_models" in data["deepfakebench"]
    assert isinstance(data["deepfakebench"]["available_models"], list)


@pytest.mark.integration
def test_model_status_unauthenticated(client):
    """Test that model status endpoint requires authentication"""
    response = client.get("/api/models/status")
    
    # Should return 401 or 403 for unauthenticated request
    assert response.status_code in [401, 403]


@pytest.mark.integration
def test_history_endpoint_authenticated(client, auth_token):
    """Test detection history endpoint with authentication"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/history", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # History returns paginated format: {total, offset, limit, jobs}
    assert isinstance(data, dict)
    assert "jobs" in data
    assert isinstance(data["jobs"], list)
    assert "total" in data
    assert "limit" in data


@pytest.mark.integration
def test_history_endpoint_unauthenticated(client):
    """Test that history endpoint requires authentication"""
    response = client.get("/api/history")
    
    # Should return 401 or 403 for unauthenticated request
    assert response.status_code in [401, 403]


@pytest.mark.integration
def test_detect_endpoint_requires_auth(client):
    """Test that detect endpoint requires authentication"""
    # Try to access without token
    response = client.post("/detect")
    
    # Should return 401 or 403 for unauthenticated request
    assert response.status_code in [401, 403, 422]  # 422 if no file provided


@pytest.mark.integration
def test_invalid_token(client):
    """Test API with invalid token"""
    headers = {"Authorization": "Bearer invalid_token_xyz"}
    response = client.get("/api/models/status", headers=headers)
    
    # Should return 401 for invalid token
    assert response.status_code == 401


@pytest.mark.integration
def test_web_pages_accessible(client):
    """Test that web pages are accessible"""
    pages = [
        "/web/login.html",
        "/web/register.html",
        "/web/index_main.html",
        "/web/history.html",
        "/web/deepfakebench.html"
    ]
    
    for page in pages:
        response = client.get(page)
        assert response.status_code == 200, f"Page {page} not accessible"


@pytest.mark.integration
@pytest.mark.slow
def test_concurrent_requests(client, auth_token):
    """Test handling of concurrent requests"""
    import concurrent.futures
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    def make_request():
        response = client.get("/api/models/status", headers=headers)
        return response.status_code == 200
    
    # Make 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # All requests should succeed
    assert all(results), "Some concurrent requests failed"

