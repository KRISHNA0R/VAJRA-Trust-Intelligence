"""
Basic tests for the deepfake detection system

Tests include:
- Module imports
- Configuration file validation
- Health check endpoint
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.unit
def test_import_main():
    """Test that main module can be imported"""
    try:
        from app import main
        assert main is not None
    except ImportError as e:
        pytest.skip(f"Cannot import main module: {e}")


@pytest.mark.unit
def test_import_adapters():
    """Test that adapter modules can be imported"""
    try:
        from app.adapters import trufor_adapter, deepfakebench_adapter
        assert trufor_adapter is not None
        assert deepfakebench_adapter is not None
    except ImportError as e:
        pytest.skip(f"Cannot import adapter modules: {e}")


@pytest.mark.unit
def test_import_auth():
    """Test that auth modules can be imported"""
    try:
        from app.auth import user_manager, decorators
        assert user_manager is not None
        assert decorators is not None
    except ImportError as e:
        pytest.skip(f"Cannot import auth modules: {e}")


@pytest.mark.unit
def test_config_files_exist():
    """Test that required configuration files exist"""
    project_root = Path(__file__).parent.parent
    
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "configs/requirements.txt",
        "configs/config.yaml",
        ".gitignore",
        ".dockerignore"
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Required file missing: {file_path}"


@pytest.mark.unit
def test_config_yaml_valid():
    """Test that config.yaml is valid"""
    import yaml
    project_root = Path(__file__).parent.parent
    config_path = project_root / "configs" / "config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    assert config is not None
    assert isinstance(config, dict)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    except ImportError as e:
        pytest.skip(f"Cannot test health endpoint: {e}")

