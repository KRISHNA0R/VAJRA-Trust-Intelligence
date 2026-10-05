"""
User Management Module
Handles user authentication, registration, and role management using local file storage
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from passlib.context import CryptContext
from jose import JWTError, jwt

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24  # Token expires after 24 hours. Change this value to adjust (e.g., 168 for 7 days, 720 for 30 days)

# File paths
DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_DIR = DATA_DIR / "sessions"
REVOKED_TOKENS_FILE = SESSIONS_DIR / "revoked_tokens.json"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserManager:
    """Manages user accounts and authentication"""

    def __init__(self):
        """Initialize user manager and ensure data files exist"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

        # Initialize users file if it doesn't exist
        if not USERS_FILE.exists():
            self._create_default_users()

        # Initialize revoked tokens file
        if not REVOKED_TOKENS_FILE.exists():
            self._save_json(REVOKED_TOKENS_FILE, {"tokens": []})

    def _create_default_users(self):
        """Create default admin user on first run"""
        default_users = {
            "users": [
                {
                    "username": "admin",
                    "password_hash": self._hash_password("admin123"),
                    "role": "admin",
                    "created_at": datetime.now().isoformat(),
                    "email": "admin@localhost"
                }
            ]
        }
        self._save_json(USERS_FILE, default_users)
        print("✓ Created default admin user (username: admin, password: admin123)")

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def _load_json(self, filepath: Path) -> dict:
        """Load JSON from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, filepath: Path, data: dict):
        """Save JSON to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_users(self) -> List[Dict]:
        """Load all users from file"""
        data = self._load_json(USERS_FILE)
        return data.get("users", [])

    def _save_users(self, users: List[Dict]):
        """Save users to file"""
        self._save_json(USERS_FILE, {"users": users})

    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        users = self._load_users()
        for user in users:
            if user["username"] == username:
                return user
        return None

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        user = self.get_user(username)
        if not user:
            return None

        if not self._verify_password(password, user["password_hash"]):
            return None

        # Return user without password hash
        user_safe = {k: v for k, v in user.items() if k != "password_hash"}
        return user_safe

    def create_user(self, username: str, password: str, role: str, email: str = "") -> Dict:
        """Create a new user"""
        # Validate role
        if role not in ["admin", "analyst", "investigator"]:
            raise ValueError("Role must be 'admin' or 'analyst' or 'investigator'")

        # Check if user already exists
        if self.get_user(username):
            raise ValueError(f"User '{username}' already exists")

        # Validate username
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters")

        # ENHANCEMENT-005: Enhanced password policy validation
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one number")

        # Create new user
        users = self._load_users()
        new_user = {
            "username": username,
            "password_hash": self._hash_password(password),
            "role": role,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }

        users.append(new_user)
        self._save_users(users)

        # Return user without password hash
        return {k: v for k, v in new_user.items() if k != "password_hash"}

    def update_user(self, username: str, **kwargs) -> Dict:
        """Update user information (excluding password)"""
        users = self._load_users()

        for i, user in enumerate(users):
            if user["username"] == username:
                # Update allowed fields
                allowed_fields = {"email", "role"}
                for key, value in kwargs.items():
                    if key in allowed_fields:
                        if key == "role" and value not in ["admin", "analyst", "investigator"]:
                            raise ValueError("Role must be 'admin' or 'analyst' or 'investigator'")
                        user[key] = value

                users[i] = user
                self._save_users(users)
                return {k: v for k, v in user.items() if k != "password_hash"}

        raise ValueError(f"User '{username}' not found")

    def change_password(self, username: str, old_password: str, new_password: str):
        """Change user password"""
        # Authenticate with old password
        if not self.authenticate_user(username, old_password):
            raise ValueError("Current password is incorrect")

        # ENHANCEMENT-005: Enhanced password policy validation
        if not new_password or len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters")
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in new_password):
            raise ValueError("New password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in new_password):
            raise ValueError("New password must contain at least one lowercase letter")
        
        # Check for at least one digit
        if not any(c.isdigit() for c in new_password):
            raise ValueError("New password must contain at least one number")

        # Update password
        users = self._load_users()
        for i, user in enumerate(users):
            if user["username"] == username:
                user["password_hash"] = self._hash_password(new_password)
                users[i] = user
                self._save_users(users)
                return True

        raise ValueError(f"User '{username}' not found")

    def delete_user(self, username: str):
        """Delete a user"""
        if username == "admin":
            raise ValueError("Cannot delete default admin user")

        users = self._load_users()
        original_count = len(users)
        users = [u for u in users if u["username"] != username]

        if len(users) == original_count:
            raise ValueError(f"User '{username}' not found")

        self._save_users(users)

    def list_users(self) -> List[Dict]:
        """List all users (without password hashes)"""
        users = self._load_users()
        return [{k: v for k, v in user.items() if k != "password_hash"} for user in users]

    def update_last_login(self, username: str):
        """Update user's last login timestamp"""
        users = self._load_users()
        for i, user in enumerate(users):
            if user["username"] == username:
                user["last_login"] = datetime.now().isoformat()
                users[i] = user
                self._save_users(users)
                break

    def create_access_token(self, username: str, role: str) -> str:
        """Create JWT access token"""
        expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        expire = datetime.utcnow() + expires_delta

        to_encode = {
            "sub": username,
            "role": role,
            "exp": expire
        }

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            # Check if token is revoked
            if self.is_token_revoked(token):
                return None

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: Optional[str] = payload.get("sub")
            role: Optional[str] = payload.get("role")

            if username is None:
                return None

            return {"username": username, "role": role}

        except JWTError:
            return None

    def revoke_token(self, token: str):
        """Add token to revoked list (for logout)"""
        revoked_data = self._load_json(REVOKED_TOKENS_FILE)
        tokens = revoked_data.get("tokens", [])

        if token not in tokens:
            tokens.append(token)
            # Keep only recent tokens (last 1000)
            if len(tokens) > 1000:
                tokens = tokens[-1000:]

            self._save_json(REVOKED_TOKENS_FILE, {"tokens": tokens})

    def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked"""
        revoked_data = self._load_json(REVOKED_TOKENS_FILE)
        tokens = revoked_data.get("tokens", [])
        return token in tokens


# Global instance
user_manager = UserManager()


# Helper functions for testing and direct use
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary containing claims (must have 'sub' key for username)
        expires_delta: Optional custom expiry time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
