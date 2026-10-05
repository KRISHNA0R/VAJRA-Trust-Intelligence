# Manual Testing Scripts

This directory contains **manual testing scripts** that are not part of the automated CI/CD pipeline.

## Purpose

These scripts are for:
- **Interactive testing** during development
- **Exploratory testing** with real server
- **Manual verification** of specific features
- **Debugging** and troubleshooting

## Important

⚠️ **These scripts are NOT run by pytest automatically**
- They require a running server (Docker or local)
- They may need model weights to be present
- They are interactive and require user input

## Available Scripts

### 1. `api_testing.py`
**Purpose**: Manual API endpoint testing

**Usage**:
```bash
# Make sure server is running
docker compose up -d

# Run the script
python tests/manual/api_testing.py
```

**Tests**:
- Health check endpoint
- User registration and login
- Model status endpoint
- Detection history endpoint

---

### 2. `model_loading.py`
**Purpose**: Manual model loading verification

**Usage**:
```bash
python tests/manual/model_loading.py
```

**Tests**:
- TruFor model loading
- DeepfakeBench model discovery
- Model building from weights

**Requirements**:
- Model weights must be present
- `models/trufor.pth.tar` exists
- DeepfakeBench weights in `models/vendors/DeepfakeBench/training/weights/`

---

## Adding New Manual Tests

When creating new manual test scripts:

1. **Place them in this directory** (`tests/manual/`)
2. **Name them descriptively** (no need to start with `test_`)
3. **Add documentation** in this README
4. **Include usage instructions**

**Example**:
```python
# tests/manual/performance_testing.py
"""
Manual performance testing script
Run with: python tests/manual/performance_testing.py
"""
```

---

## Why Separate from Automated Tests?

**Automated Tests** (`tests/*.py`):
- ✅ Run by pytest in CI/CD
- ✅ Fast and isolated
- ✅ No external dependencies
- ✅ Exit with clear pass/fail

**Manual Tests** (`tests/manual/*.py`):
- 🔧 Require running server
- 🔧 Interactive user input
- 🔧 May need model weights
- 🔧 Exploratory in nature

---

## Directory Structure

```
tests/
├── __init__.py
├── test_basic.py           # Automated: Module imports, config
├── test_integration.py     # Automated: API endpoints
├── test_auth.py            # Automated: Authentication
├── test_history.py         # Automated: History management
├── test_adapters.py        # Automated: Model adapters
└── manual/                 # Manual testing scripts
    ├── README.md           # This file
    ├── api_testing.py      # Manual: API endpoint testing
    └── model_loading.py    # Manual: Model loading tests
```

---

**Last Updated**: October 26, 2025  
**Maintained by**: Xiyu Guan

