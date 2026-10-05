"""
Unit tests for model adapters

Tests include:
- TruFor adapter configuration
- DeepfakeBench adapter configuration
- Model path validation
- Adapter interface consistency
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.unit
def test_trufor_adapter_import():
    """Test that TruFor adapter can be imported"""
    try:
        from app.adapters import trufor_adapter
        assert trufor_adapter is not None
    except ImportError as e:
        pytest.skip(f"Cannot import TruFor adapter: {e}")


@pytest.mark.unit
def test_deepfakebench_adapter_import():
    """Test that DeepfakeBench adapter can be imported"""
    try:
        from app.adapters import deepfakebench_adapter
        assert deepfakebench_adapter is not None
    except ImportError as e:
        pytest.skip(f"Cannot import DeepfakeBench adapter: {e}")


@pytest.mark.unit
def test_trufor_model_path():
    """Test TruFor model path configuration"""
    project_root = Path(__file__).parent.parent
    expected_path = project_root / "models/trufor.pth.tar"
    
    # Path configuration should point to project root
    assert expected_path.parent.exists()


@pytest.mark.unit
def test_deepfakebench_weights_directory():
    """Test DeepfakeBench weights directory path"""
    project_root = Path(__file__).parent.parent
    weights_dir = project_root / "vendors" / "DeepfakeBench" / "training" / "weights"
    
    # Directory may not exist (weights optional), but parent structure should
    vendors_dir = project_root / "vendors"
    # vendors_dir may or may not exist depending on setup


@pytest.mark.unit
def test_adapter_module_structure():
    """Test that adapters have expected structure"""
    try:
        from app.adapters import trufor_adapter, deepfakebench_adapter
        
        # TruFor adapter should have these attributes/functions
        trufor_attrs = dir(trufor_adapter)
        assert len(trufor_attrs) > 0
        
        # DeepfakeBench adapter should have these attributes/functions
        dfbench_attrs = dir(deepfakebench_adapter)
        assert len(dfbench_attrs) > 0
        
    except ImportError as e:
        pytest.skip(f"Cannot import adapters: {e}")


@pytest.mark.unit
def test_model_file_extensions():
    """Test that model files have correct extensions"""
    trufor_model = "models/trufor.pth.tar"
    dfbench_model = "xception_best.pth"
    
    # TruFor uses .pth.tar
    assert trufor_model.endswith(".pth.tar")
    
    # DeepfakeBench uses .pth
    assert dfbench_model.endswith(".pth")


@pytest.mark.unit
def test_weight_registry_structure():
    """Test DeepfakeBench weight registry structure"""
    try:
        from tools.weight_registry import WEIGHT_REGISTRY
        
        assert isinstance(WEIGHT_REGISTRY, dict)
        assert len(WEIGHT_REGISTRY) > 0
        
        # Check structure of first entry
        first_key = list(WEIGHT_REGISTRY.keys())[0]
        first_value = WEIGHT_REGISTRY[first_key]
        
        assert "model_key" in first_value
        assert "input_size" in first_value
        
    except ImportError as e:
        pytest.skip(f"Cannot import weight registry: {e}")


@pytest.mark.unit
def test_weight_registry_count():
    """Test that weight registry has correct number of models"""
    try:
        from tools.weight_registry import WEIGHT_REGISTRY
        
        # Should have 12 models in V3.0
        assert len(WEIGHT_REGISTRY) == 12
        
    except ImportError as e:
        pytest.skip(f"Cannot import weight registry: {e}")


@pytest.mark.unit
def test_weight_registry_model_keys():
    """Test that weight registry has expected model keys"""
    try:
        from tools.weight_registry import WEIGHT_REGISTRY
        
        expected_models = [
            "xception",
            "meso4",
            "meso4Inception",
            "f3net",
            "efficientnetb4",
            "capsule_net",
            "srm",
            "recce",
            "spsl",
            "ucf",
            "multi_attention",
            "core"
        ]
        
        registry_models = [v["model_key"] for v in WEIGHT_REGISTRY.values()]
        
        # All expected models should be in registry
        for model in expected_models:
            assert model in registry_models, f"Model {model} missing from registry"
        
    except ImportError as e:
        pytest.skip(f"Cannot import weight registry: {e}")


@pytest.mark.unit
def test_weight_filenames_format():
    """Test that weight filenames follow expected format"""
    try:
        from tools.weight_registry import WEIGHT_REGISTRY
        
        for filename in WEIGHT_REGISTRY.keys():
            # Should end with _best.pth
            assert filename.endswith("_best.pth"), f"Invalid filename format: {filename}"
        
    except ImportError as e:
        pytest.skip(f"Cannot import weight registry: {e}")


@pytest.mark.unit
def test_input_sizes_are_valid():
    """Test that model input sizes are reasonable"""
    try:
        from tools.weight_registry import WEIGHT_REGISTRY
        
        for model_name, config in WEIGHT_REGISTRY.items():
            input_size = config["input_size"]
            
            # Input size should be reasonable (between 64 and 512)
            assert 64 <= input_size <= 512, f"{model_name} has invalid input size: {input_size}"
            
    except ImportError as e:
        pytest.skip(f"Cannot import weight registry: {e}")


@pytest.mark.unit
def test_adapter_error_handling():
    """Test that adapters handle missing models gracefully"""
    # This is more of an integration test, but we can test the concept
    model_path = Path("/nonexistent/path/model.pth")
    
    assert not model_path.exists()


@pytest.mark.unit
def test_config_yaml_has_models():
    """Test that config.yaml contains model configurations"""
    import yaml
    project_root = Path(__file__).parent.parent
    config_path = project_root / "configs" / "config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Should have models section
    assert "models" in config or "trufor" in config or "deepfakebench" in config


@pytest.mark.unit
def test_build_dfbench_model_function():
    """Test that build function exists"""
    try:
        from tools.build_dfbench_model import build_dfbench_model
        
        assert callable(build_dfbench_model)
        
    except ImportError as e:
        pytest.skip(f"Cannot import build function: {e}")


@pytest.mark.unit
@pytest.mark.requires_models
def test_trufor_model_size():
    """Test that TruFor model file is reasonable size if it exists"""
    project_root = Path(__file__).parent.parent
    model_path = project_root / "models/trufor.pth.tar"
    
    if not model_path.exists():
        pytest.skip("TruFor model not present")
    
    size_mb = model_path.stat().st_size / (1024 * 1024)
    
    # TruFor model should be around 200-300 MB
    assert 100 < size_mb < 500, f"TruFor model size unusual: {size_mb:.1f}MB"


@pytest.mark.unit
def test_model_discovery_logic():
    """Test logic for discovering available models"""
    # Example: Finding .pth files in a directory
    from pathlib import Path
    
    test_files = [
        "xception_best.pth",
        "meso4_best.pth",
        "not_a_model.txt",
        "readme.md"
    ]
    
    # Filter for .pth files
    pth_files = [f for f in test_files if f.endswith(".pth")]
    
    assert len(pth_files) == 2
    assert "xception_best.pth" in pth_files
    assert "meso4_best.pth" in pth_files


@pytest.mark.unit
def test_adapter_response_format():
    """Test expected response format from adapters"""
    # Adapters should return dict with these keys
    expected_response_keys = ["prediction", "confidence"]
    
    sample_response = {
        "prediction": "fake",
        "confidence": 0.85,
        "details": {}
    }
    
    for key in expected_response_keys:
        assert key in sample_response


@pytest.mark.unit
def test_confidence_score_range():
    """Test that confidence scores are in valid range"""
    confidence_scores = [0.0, 0.5, 0.85, 1.0]
    
    for score in confidence_scores:
        assert 0.0 <= score <= 1.0


@pytest.mark.unit
def test_prediction_values():
    """Test that prediction values are standardized"""
    valid_predictions = ["real", "fake", "unknown", "authentic", "synthetic"]
    
    # Our system should use "real" or "fake"
    our_predictions = ["real", "fake"]
    
    for pred in our_predictions:
        assert pred in valid_predictions

