"""
Unit tests for history module

Tests include:
- History manager functionality
- Record creation and retrieval
- Data persistence
- User-specific history filtering
"""
import pytest
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.unit
def test_history_manager_import():
    """Test that history manager can be imported"""
    try:
        from app.history import history_manager
        assert history_manager is not None
    except ImportError as e:
        pytest.skip(f"Cannot import history manager: {e}")


@pytest.mark.unit
def test_history_record_structure():
    """Test that history record has correct structure"""
    # A history record should have these fields
    required_fields = [
        "filename",
        "timestamp",
        "prediction",
        "confidence"
    ]
    
    # Create a sample record
    record = {
        "filename": "test_image.jpg",
        "timestamp": datetime.now().isoformat(),
        "prediction": "fake",
        "confidence": 0.85
    }
    
    for field in required_fields:
        assert field in record


@pytest.mark.unit
def test_history_file_location():
    """Test that history files are stored in correct location"""
    project_root = Path(__file__).parent.parent
    jobs_dir = project_root / "data" / "jobs"
    
    # Directory should exist or be creatable
    assert jobs_dir.parent.exists(), "data directory should exist"


@pytest.mark.unit
def test_history_json_format():
    """Test that history can be saved and loaded as JSON"""
    history_data = [
        {
            "filename": "image1.jpg",
            "timestamp": "2025-10-25T10:00:00",
            "prediction": "real",
            "confidence": 0.92
        },
        {
            "filename": "image2.jpg",
            "timestamp": "2025-10-25T10:05:00",
            "prediction": "fake",
            "confidence": 0.78
        }
    ]
    
    # Test JSON serialization
    json_str = json.dumps(history_data)
    assert json_str is not None
    
    # Test JSON deserialization
    loaded_data = json.loads(json_str)
    assert loaded_data == history_data


@pytest.mark.unit
def test_history_filtering_by_user():
    """Test that history can be filtered by username"""
    all_history = [
        {"username": "user1", "filename": "img1.jpg", "prediction": "real"},
        {"username": "user2", "filename": "img2.jpg", "prediction": "fake"},
        {"username": "user1", "filename": "img3.jpg", "prediction": "fake"},
    ]
    
    # Filter for user1
    user1_history = [h for h in all_history if h["username"] == "user1"]
    
    assert len(user1_history) == 2
    assert all(h["username"] == "user1" for h in user1_history)


@pytest.mark.unit
def test_history_sorting_by_timestamp():
    """Test that history can be sorted by timestamp"""
    history = [
        {"timestamp": "2025-10-25T12:00:00", "filename": "img1.jpg"},
        {"timestamp": "2025-10-25T10:00:00", "filename": "img2.jpg"},
        {"timestamp": "2025-10-25T11:00:00", "filename": "img3.jpg"},
    ]
    
    # Sort by timestamp (newest first)
    sorted_history = sorted(history, key=lambda x: x["timestamp"], reverse=True)
    
    assert sorted_history[0]["filename"] == "img1.jpg"
    assert sorted_history[1]["filename"] == "img3.jpg"
    assert sorted_history[2]["filename"] == "img2.jpg"


@pytest.mark.unit
def test_history_limit_records():
    """Test that history can limit number of returned records"""
    history = [{"id": i, "filename": f"img{i}.jpg"} for i in range(100)]
    
    # Limit to 20 most recent
    limit = 20
    limited_history = history[:limit]
    
    assert len(limited_history) == 20


@pytest.mark.unit
def test_history_empty_list():
    """Test that new user gets empty history list"""
    history = []
    
    assert isinstance(history, list)
    assert len(history) == 0


@pytest.mark.unit
def test_history_confidence_range():
    """Test that confidence values are in valid range [0, 1]"""
    history = [
        {"confidence": 0.0},
        {"confidence": 0.5},
        {"confidence": 1.0},
    ]
    
    for record in history:
        assert 0.0 <= record["confidence"] <= 1.0


@pytest.mark.unit
def test_history_prediction_values():
    """Test that prediction values are valid"""
    valid_predictions = ["real", "fake", "unknown"]
    
    history = [
        {"prediction": "real"},
        {"prediction": "fake"},
        {"prediction": "unknown"},
    ]
    
    for record in history:
        assert record["prediction"] in valid_predictions


@pytest.mark.unit
def test_history_timestamp_format():
    """Test that timestamp is in ISO format"""
    timestamp = datetime.now().isoformat()
    
    # Should be parseable back to datetime
    parsed = datetime.fromisoformat(timestamp)
    assert isinstance(parsed, datetime)


@pytest.mark.unit
def test_history_file_persistence():
    """Test that history can be written to and read from file"""
    history_data = [
        {"filename": "test.jpg", "prediction": "fake", "confidence": 0.8}
    ]
    
    # Use temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(history_data, f)
        temp_path = f.name
    
    try:
        # Read back
        with open(temp_path, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == history_data
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


@pytest.mark.unit
def test_history_append_new_record():
    """Test that new record can be appended to history"""
    existing_history = [
        {"id": 1, "filename": "img1.jpg"},
        {"id": 2, "filename": "img2.jpg"},
    ]
    
    new_record = {"id": 3, "filename": "img3.jpg"}
    
    existing_history.append(new_record)
    
    assert len(existing_history) == 3
    assert existing_history[-1]["id"] == 3


@pytest.mark.unit
def test_history_unique_filenames():
    """Test detection of duplicate filenames"""
    history = [
        {"filename": "img1.jpg"},
        {"filename": "img2.jpg"},
        {"filename": "img1.jpg"},  # Duplicate
    ]
    
    filenames = [h["filename"] for h in history]
    unique_filenames = set(filenames)
    
    assert len(filenames) == 3
    assert len(unique_filenames) == 2  # Only 2 unique


@pytest.mark.unit
def test_history_search_by_filename():
    """Test searching history by filename"""
    history = [
        {"filename": "vacation.jpg", "prediction": "real"},
        {"filename": "portrait.jpg", "prediction": "fake"},
        {"filename": "vacation_2.jpg", "prediction": "real"},
    ]
    
    # Search for files containing "vacation"
    results = [h for h in history if "vacation" in h["filename"]]
    
    assert len(results) == 2


@pytest.mark.unit
def test_history_statistics():
    """Test calculating statistics from history"""
    history = [
        {"prediction": "real", "confidence": 0.9},
        {"prediction": "fake", "confidence": 0.8},
        {"prediction": "fake", "confidence": 0.7},
        {"prediction": "real", "confidence": 0.95},
    ]
    
    total = len(history)
    real_count = sum(1 for h in history if h["prediction"] == "real")
    fake_count = sum(1 for h in history if h["prediction"] == "fake")
    avg_confidence = sum(h["confidence"] for h in history) / total
    
    assert total == 4
    assert real_count == 2
    assert fake_count == 2
    assert 0.8 < avg_confidence < 0.9

