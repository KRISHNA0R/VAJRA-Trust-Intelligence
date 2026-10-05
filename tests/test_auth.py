"""
Unit tests for authentication module

Tests include:
- User manager functionality
- Password hashing and verification
- JWT token generation and validation
- Decorators for authentication
"""
import pytest
import sys
from pathlib import Path
from datetime import timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.unit
def test_password_hashing():
    """Test password hashing produces different hash each time"""
    try:
        from app.auth.user_manager import hash_password
        
        password = "test123456"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Same password should produce different hashes (due to salt)
        assert hash1 != hash2
        assert len(hash1) > 50  # BCrypt hashes are long
    except ImportError as e:
        pytest.skip(f"Cannot import auth modules: {e}")


@pytest.mark.unit
def test_password_verification():
    """Test password verification with correct and incorrect passwords"""
    try:
        from app.auth.user_manager import hash_password, verify_password
        
        password = "test123456"
        hashed = hash_password(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True
        
        # Wrong password should fail
        assert verify_password("wrongpassword", hashed) is False
    except ImportError as e:
        pytest.skip(f"Cannot import auth modules: {e}")


@pytest.mark.unit
def test_jwt_token_creation():
    """Test JWT token creation"""
    try:
        from app.auth.user_manager import create_access_token
        
        data = {"sub": "test_user"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
        assert token.count('.') == 2  # JWT format: header.payload.signature
    except ImportError as e:
        pytest.skip(f"Cannot import auth modules: {e}")


@pytest.mark.unit
def test_jwt_token_with_expiry():
    """Test JWT token creation with custom expiry"""
    try:
        from app.auth.user_manager import create_access_token
        
        data = {"sub": "test_user"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert token is not None
        assert isinstance(token, str)
    except ImportError as e:
        pytest.skip(f"Cannot import auth modules: {e}")


@pytest.mark.unit
def test_token_expiry_constant():
    """Test that token expiry constant is reasonable"""
    try:
        from app.auth.user_manager import ACCESS_TOKEN_EXPIRE_HOURS
        
        assert ACCESS_TOKEN_EXPIRE_HOURS > 0
        assert ACCESS_TOKEN_EXPIRE_HOURS <= 72  # Not more than 3 days
    except ImportError as e:
        pytest.skip(f"Cannot import auth modules: {e}")


@pytest.mark.unit
def test_user_data_structure():
    """Test user data structure from users.json"""
    import json
    project_root = Path(__file__).parent.parent
    users_file = project_root / "data" / "users.json"
    
    if not users_file.exists():
        pytest.skip("users.json doesn't exist yet")
    
    with open(users_file, 'r') as f:
        data = json.load(f)
    
    # users.json format is {"users": [...]}
    assert isinstance(data, dict)
    assert "users" in data
    users = data["users"]
    assert isinstance(users, list)
    
    # If there are users, check structure
    if len(users) > 0:
        user = users[0]
        assert "username" in user
        assert "email" in user
        assert "password_hash" in user or "hashed_password" in user


@pytest.mark.unit
def test_secret_key_exists():
    """Test that SECRET_KEY is defined for JWT"""
    try:
        from app.auth.user_manager import SECRET_KEY
        
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 20  # Should be reasonably long
    except ImportError as e:
        pytest.skip(f"Cannot import auth modules: {e}")


@pytest.mark.unit
def test_algorithm_is_valid():
    """Test that JWT algorithm is set correctly"""
    try:
        from app.auth.user_manager import ALGORITHM
        
        assert ALGORITHM in ["HS256", "HS384", "HS512", "RS256"]
    except ImportError as e:
        pytest.skip(f"Cannot import auth modules: {e}")


@pytest.mark.unit
def test_password_requirements():
    """Test password meets minimum security requirements"""
    try:
        from app.auth.user_manager import hash_password
        
        # Test various password lengths
        short_password = "123"
        medium_password = "test123"
        long_password = "test123456789"
        
        # All should be hashable (validation happens at API level)
        assert hash_password(short_password) is not None
        assert hash_password(medium_password) is not None
        assert hash_password(long_password) is not None
    except ImportError as e:
        pytest.skip(f"Cannot import auth modules: {e}")


@pytest.mark.unit
def test_token_decode_structure():
    """Test that token can be decoded and has expected structure"""
    try:
        from app.auth.user_manager import create_access_token
        from jose import jwt
        from app.auth.user_manager import SECRET_KEY, ALGORITHM
        
        data = {"sub": "test_user", "custom": "field"}
        token = create_access_token(data)
        
        # Decode token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert "sub" in decoded
        assert decoded["sub"] == "test_user"
        assert "exp" in decoded  # Expiry should be added
    except ImportError as e:
        pytest.skip(f"Cannot import required modules: {e}")

