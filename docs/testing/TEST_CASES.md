# Test Cases Documentation

**Project**: Deepfake Detector  
**Document Version**: 2.0  
**Last Updated**: October 26, 2025  
**Author**: Xiyu Guan

## Document Purpose

This document provides a comprehensive list of all test cases for the Deepfake Detection System, including:
- Pass/Fail scenarios
- Edge cases and boundary conditions
- Expected results and validation criteria
- Test data requirements

## Test Execution Status

**Cycle 1 Completed** (October 25-26, 2025):
- ✅ **67 automated tests executed** (100% pass rate)
- ✅ **Code Coverage**: 70% (exceeded 60% target)
- ✅ **Test Environment**: Local (Windows) + CI (Ubuntu)
- ✅ **All critical test cases passed**

**Test Files Implemented**:
- `tests/test_basic.py` - 3 unit tests ✅
- `tests/test_auth.py` - 10 auth tests ✅
- `tests/test_integration.py` - 10 integration tests ✅
- `tests/test_history.py` - 16 history tests ✅
- `tests/test_adapters.py` - 26 adapter tests ✅
- **Manual scripts**: `tests/manual/` - 2 scripts (not automated)

### Cycle 1 Test Cases Status Quick Reference

| Test ID | Test Name | Status | Test File |
|---------|-----------|--------|-----------|
| TC-U-001 | Module Import Test | ✅ Pass | test_basic.py |
| TC-U-002 | Configuration File Validation | ✅ Pass | test_basic.py |
| TC-U-003 | Config YAML Structure | ✅ Pass | test_basic.py |
| TC-I-001 | Health Check Endpoint | ✅ Pass | test_integration.py |
| TC-I-002 | Web Pages Accessibility | ✅ Pass | test_integration.py |
| TC-A-001 | User Registration - Success | ✅ Pass | test_integration.py |
| TC-A-003 | User Login - Valid | ✅ Pass | test_integration.py |
| TC-A-004 | User Login - Invalid | ✅ Pass | test_integration.py |
| TC-A-005 | Token Validation - Valid | ✅ Pass | test_integration.py |
| TC-A-006 | Token Validation - Invalid | ✅ Pass | test_integration.py |
| TC-A-007 | Protected Endpoint - No Token | ✅ Pass | test_integration.py |
| TC-E-001 | Model Status Endpoint | ✅ Pass | test_integration.py |
| TC-E-002 | History Endpoint - Empty | ✅ Pass | test_integration.py |
| TC-M-001 | TruFor Model Loading | ⏭️ Skipped | Requires weights |
| TC-M-002 | TruFor Missing Weights | ✅ Pass | test_adapters.py |
| TC-M-003 | DeepfakeBench Discovery | ✅ Pass | test_adapters.py |
| TC-M-004 | DeepfakeBench Building | ⏭️ Skipped | Requires weights |
| TC-E-003 | Detection - No File | 🟡 Not Run | Cycle 2 |
| TC-E-101 to TC-E-106 | Edge Cases | 🟡 Not Run | Cycle 2/3 |
| TC-P-001, TC-P-002 | Performance Tests | 🟡 Not Run | Cycle 3 |

**Legend**:
- ✅ Pass - Test executed and passed
- ⏭️ Skipped - Test skipped (expected, requires model weights)
- 🟡 Not Run - Not executed in Cycle 1 (planned for later cycles)
- ❌ Fail - Test failed (none in Cycle 1)

**Additional Tests** (not in detailed test cases below):
- 16 History Management tests ✅
- 24 Additional Adapter tests ✅

---

## Test Case Categories

1. [Unit Tests](#1-unit-tests)
2. [Integration Tests](#2-integration-tests)
3. [Authentication Tests](#3-authentication-tests)
4. [Model Loading Tests](#4-model-loading-tests)
5. [API Endpoint Tests](#5-api-endpoint-tests)
6. [Edge Cases and Error Handling](#6-edge-cases-and-error-handling)
7. [Performance Tests](#7-performance-tests)

---

## 1. Unit Tests

### TC-U-001: Module Import Test
**Objective**: Verify that all core modules can be imported without errors

**Preconditions**: Python environment is properly set up

**Test Steps**:
1. Import `app.main` module
2. Import `app.adapters.trufor_adapter` module
3. Import `app.adapters.deepfakebench_adapter` module
4. Import `app.auth.user_manager` module
5. Import `app.auth.decorators` module

**Expected Result**: ✅ All modules import successfully without ImportError

**Actual Result**: ✅ All core modules imported successfully (Cycle 1 - Oct 26, 2025)

**Status**: ✅ Pass

**Priority**: High  
**Test Type**: Unit  
**Automated**: Yes  
**Test File**: `tests/test_basic.py::test_import_main`

---

### TC-U-002: Configuration File Validation
**Objective**: Verify that all required configuration files exist and are valid

**Preconditions**: Project is properly cloned

**Test Steps**:
1. Check existence of `Dockerfile`
2. Check existence of `docker-compose.yml`
3. Check existence of `configs/requirements.txt`
4. Check existence of `configs/config.yaml`
5. Check existence of `.gitignore`
6. Check existence of `.dockerignore`
7. Parse and validate `configs/config.yaml` as valid YAML

**Expected Result**: 
- ✅ All files exist
- ✅ YAML files are properly formatted

**Actual Result**: ✅ All configuration files exist and valid (Cycle 1 - Oct 26, 2025)

**Status**: ✅ Pass

**Priority**: High  
**Test Type**: Unit  
**Automated**: Yes  
**Test File**: `tests/test_basic.py::test_config_files_exist`, `test_config_yaml_valid`

---

### TC-U-003: Config YAML Structure Validation
**Objective**: Verify config.yaml has correct structure and required keys

**Preconditions**: config.yaml exists

**Test Steps**:
1. Load config.yaml
2. Verify it's a dictionary
3. Check for required keys: `models`, `server`, etc.

**Expected Result**: ✅ Config has correct structure

**Actual Result**: ✅ Config YAML structure validated successfully (Cycle 1 - Oct 26, 2025)

**Status**: ✅ Pass

**Priority**: Medium  
**Test Type**: Unit  
**Automated**: Yes  
**Test File**: `tests/test_basic.py::test_config_yaml_valid`

---

## 2. Integration Tests

### TC-I-001: Health Check Endpoint
**Objective**: Verify the health check endpoint returns correct status

**Preconditions**: FastAPI application is running

**Test Steps**:
1. Send GET request to `/health`
2. Check HTTP status code
3. Verify response JSON structure
4. Verify `status` field equals "healthy"
5. Verify `timestamp` field is present

**Expected Result**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T10:00:00"
}
```

**Actual Result**: ✅ Health endpoint returns correct status and structure (Cycle 1 - Oct 26, 2025)

**Status**: ✅ Pass

**Priority**: High  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_health_endpoint`

---

### TC-I-002: Web Pages Accessibility
**Objective**: Verify all web pages are accessible

**Preconditions**: Server is running

**Test Steps**:
1. GET `/web/login.html` → expect 200
2. GET `/web/register.html` → expect 200
3. GET `/web/index_main.html` → expect 200
4. GET `/web/history.html` → expect 200
5. GET `/web/deepfakebench.html` → expect 200

**Expected Result**: ✅ All pages return HTTP 200

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_web_pages_accessible`

---

## 3. Authentication Tests

### TC-A-001: User Registration - Success
**Objective**: Successfully register a new user

**Preconditions**: Server is running, username doesn't exist

**Test Steps**:
1. Prepare registration data:
   ```json
   {
     "username": "test_user_12345",
     "password": "test123456",
     "email": "test@example.com"
   }
   ```
2. POST to `/register`
3. Verify HTTP 200 response
4. Verify response contains success message

**Expected Result**: ✅ User registered successfully

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_register_user`

---

### TC-A-002: User Registration - Duplicate Username
**Objective**: Verify system rejects duplicate username

**Preconditions**: User already exists

**Test Steps**:
1. Register user "test_user_xyz" (first time)
2. Try to register same username again
3. Verify appropriate error response (400 or 409)

**Expected Result**: ❌ Registration fails with appropriate error

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Medium  
**Test Type**: Integration  
**Automated**: Partial  
**Notes**: Edge case for duplicate handling

---

### TC-A-003: User Login - Valid Credentials
**Objective**: Successfully login with valid credentials

**Preconditions**: User is registered

**Test Steps**:
1. POST to `/token` with form data:
   ```
   username: test_user_12345
   password: test123456
   ```
2. Verify HTTP 200 response
3. Verify response contains:
   - `access_token`
   - `token_type: "bearer"`

**Expected Result**: ✅ Login successful, token returned

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_login_success`

---

### TC-A-004: User Login - Invalid Credentials
**Objective**: Verify login fails with wrong password

**Preconditions**: Server is running

**Test Steps**:
1. POST to `/token` with:
   ```
   username: nonexistent_user
   password: wrongpassword
   ```
2. Verify HTTP 401 response

**Expected Result**: ❌ Login fails with 401 Unauthorized

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_login_invalid_credentials`

---

### TC-A-005: Token Validation - Valid Token
**Objective**: Verify API accepts valid JWT token

**Preconditions**: User logged in with valid token

**Test Steps**:
1. Login and get token
2. Make request to `/api/models/status` with token
3. Verify HTTP 200 response

**Expected Result**: ✅ Request succeeds with valid token

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_model_status_authenticated`

---

### TC-A-006: Token Validation - Invalid Token
**Objective**: Verify API rejects invalid JWT token

**Preconditions**: Server is running

**Test Steps**:
1. Make request to `/api/models/status` with:
   ```
   Authorization: Bearer invalid_token_xyz
   ```
2. Verify HTTP 401 response

**Expected Result**: ❌ Request rejected with 401

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_invalid_token`

---

### TC-A-007: Protected Endpoint - No Token
**Objective**: Verify protected endpoints require authentication

**Preconditions**: Server is running

**Test Steps**:
1. GET `/api/models/status` without Authorization header
2. GET `/api/history` without Authorization header
3. POST `/detect` without Authorization header

**Expected Result**: ❌ All requests return 401/403

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_model_status_unauthenticated`

---

## 4. Model Loading Tests

### TC-M-001: TruFor Model Loading - Success
**Objective**: Verify TruFor model loads successfully when weights present

**Preconditions**: `trufor.pth.tar` exists in project root

**Test Steps**:
1. Attempt to load TruFor model
2. Check model object is not None
3. Verify model is in evaluation mode

**Expected Result**: ✅ Model loads successfully

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Unit (requires model weights)  
**Automated**: Yes  
**Test File**: `tests/test_model_loading.py`

---

### TC-M-002: TruFor Model Loading - Missing Weights
**Objective**: Verify graceful handling when weights are missing

**Preconditions**: `trufor.pth.tar` does NOT exist

**Test Steps**:
1. Attempt to load TruFor model
2. Verify appropriate error handling
3. Check system doesn't crash

**Expected Result**: ⚠️ Error logged, system continues

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Medium  
**Test Type**: Unit  
**Automated**: Yes  
**Test File**: `tests/test_model_loading.py`

---

### TC-M-003: DeepfakeBench Model Discovery
**Objective**: Verify system discovers available DeepfakeBench models

**Preconditions**: Some or all model weights present

**Test Steps**:
1. Scan `vendors/DeepfakeBench/training/weights/` directory
2. Match found weights with registry
3. Verify count matches expected (0-12)

**Expected Result**: ✅ Correct number of models discovered

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Unit  
**Automated**: Yes  
**Test File**: `tests/test_model_loading.py`

---

### TC-M-004: DeepfakeBench Model Building
**Objective**: Verify specific model can be built from weights

**Preconditions**: At least one model weight exists (e.g., `xception_best.pth`)

**Test Steps**:
1. Call `build_dfbench_model("xception")`
2. Verify model object returned
3. Check model has expected attributes

**Expected Result**: ✅ Model builds successfully

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Unit (requires model weights)  
**Automated**: Yes  
**Test File**: `tests/test_model_loading.py`

---

## 5. API Endpoint Tests

### TC-E-001: Model Status Endpoint Structure
**Objective**: Verify `/api/models/status` returns correct structure

**Preconditions**: User authenticated

**Test Steps**:
1. GET `/api/models/status` with valid token
2. Verify response structure:
   ```json
   {
     "trufor": {
       "available": bool,
       "path": string
     },
     "deepfakebench": {
       "available_models": [array]
     }
   }
   ```

**Expected Result**: ✅ Correct JSON structure

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_model_status_authenticated`

---

### TC-E-002: History Endpoint - Empty History
**Objective**: Verify history endpoint returns empty array for new user

**Preconditions**: New user with no detections

**Test Steps**:
1. Register new user
2. Login and get token
3. GET `/api/history` with token
4. Verify response is `[]`

**Expected Result**: ✅ Returns empty array `[]`

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Medium  
**Test Type**: Integration  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_history_endpoint_authenticated`

---

### TC-E-003: Detection Endpoint - No File
**Objective**: Verify detect endpoint validates file presence

**Preconditions**: User authenticated

**Test Steps**:
1. POST `/detect` with valid token but no file
2. Verify appropriate error response (422 or 400)

**Expected Result**: ❌ Request fails with validation error

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Medium  
**Test Type**: Integration  
**Automated**: Partial  
**Notes**: Requires file upload handling

---

## 6. Edge Cases and Error Handling

### TC-E-101: Concurrent Requests
**Objective**: Verify system handles multiple simultaneous requests

**Preconditions**: User authenticated

**Test Steps**:
1. Send 10 concurrent requests to `/api/models/status`
2. Verify all return 200
3. Check response times are reasonable

**Expected Result**: ✅ All requests succeed

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Medium  
**Test Type**: Performance  
**Automated**: Yes  
**Test File**: `tests/test_integration.py::test_concurrent_requests`

---

### TC-E-102: Large File Upload
**Objective**: Verify handling of large image/video files

**Preconditions**: User authenticated, large file prepared (>50MB)

**Test Steps**:
1. POST `/detect` with 50MB+ file
2. Verify timeout handling
3. Check appropriate error message

**Expected Result**: ⚠️ Graceful handling with timeout message

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Low  
**Test Type**: Integration  
**Automated**: No  
**Notes**: Manual test required

---

### TC-E-103: Invalid File Format
**Objective**: Verify rejection of unsupported file types

**Preconditions**: User authenticated

**Test Steps**:
1. POST `/detect` with .txt file
2. POST `/detect` with .exe file
3. Verify appropriate error messages

**Expected Result**: ❌ Files rejected with clear error

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Medium  
**Test Type**: Integration  
**Automated**: No  
**Notes**: Requires file upload handling

---

### TC-E-104: Special Characters in Username
**Objective**: Verify handling of special characters

**Preconditions**: Server running

**Test Steps**:
1. Try to register with username: `test@user!#$`
2. Verify validation or sanitization

**Expected Result**: ⚠️ Rejected or sanitized

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Low  
**Test Type**: Integration  
**Automated**: No  
**Notes**: Edge case

---

### TC-E-105: SQL Injection Attempt
**Objective**: Verify protection against SQL injection (though using JSON storage)

**Preconditions**: Server running

**Test Steps**:
1. Try registration with username: `admin' OR '1'='1`
2. Verify proper escaping/rejection

**Expected Result**: ✅ No injection, proper handling

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Security  
**Automated**: No  
**Notes**: Manual security test

---

### TC-E-106: XSS Attack Attempt
**Objective**: Verify protection against XSS in web interface

**Preconditions**: User can input text

**Test Steps**:
1. Try to register with username: `<script>alert('XSS')</script>`
2. Login and check history page
3. Verify script doesn't execute

**Expected Result**: ✅ Script escaped/sanitized

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: High  
**Test Type**: Security  
**Automated**: No  
**Notes**: Manual security test

---

## 7. Performance Tests

### TC-P-001: TruFor Inference Time
**Objective**: Measure TruFor detection time on standard image

**Preconditions**: TruFor loaded, test image (1920x1080)

**Test Steps**:
1. Upload test image to `/detect`
2. Measure response time
3. Verify < 30 seconds

**Expected Result**: ✅ Response in < 30s

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Medium  
**Test Type**: Performance  
**Automated**: No  
**Notes**: Manual test with timer

---

### TC-P-002: DeepfakeBench Video Analysis Time
**Objective**: Measure video analysis time

**Preconditions**: DeepfakeBench model loaded, test video (10s, 30fps)

**Test Steps**:
1. Upload test video
2. Measure total analysis time
3. Verify reasonable performance

**Expected Result**: ✅ Completes within expected time

**Actual Result**: _To be filled during test execution_

**Status**: 🟡 Not Run | ✅ Pass | ❌ Fail

**Priority**: Medium  
**Test Type**: Performance  
**Automated**: No  
**Notes**: Manual test with timer

---

## Test Summary

### Documented Test Cases (28 test cases in this document)

**By Priority**:
- **High**: 17 test cases
- **Medium**: 9 test cases  
- **Low**: 2 test cases

**By Type**:
- **Unit**: 5 test cases
- **Integration**: 17 test cases
- **Performance**: 3 test cases
- **Security**: 2 test cases

**By Automation Status**:
- **Fully Automated**: 18 test cases
- **Partially Automated**: 2 test cases
- **Manual Only**: 8 test cases

### Actual Execution (Cycle 1: Oct 25-26, 2025)

**Executed**: 67 automated pytest tests

**By Category**:
- **Unit Tests**: 3 tests (Module imports, Config validation) ✅
- **Authentication Tests**: 10 tests (Registration, Login, JWT) ✅
- **Integration Tests**: 10 tests (API endpoints, Protected routes) ✅
- **History Management**: 16 tests (CRUD operations, Filtering) ✅
- **Model Adapters**: 26 tests (Weight registry, Model discovery) ✅
- **Manual Scripts**: 2 scripts (API testing, Model loading) 🔧

**Test Results**:
- **Passed**: 67 tests (100%)
- **Failed**: 0 tests (0%)
- **Skipped**: 2 tests (require model weights)
- **Code Coverage**: 70%

**Test Environment**:
- **Local**: Windows 10/11, pytest (~12s execution)
- **CI**: GitHub Actions, Ubuntu Latest (~4min pipeline)

**Documentation**:
- Full results: [test_reports/cycle_1_report.md](test_reports/cycle_1_report.md)
- Test plan: [test_plans/cycle_1_basic_functionality.md](test_plans/cycle_1_basic_functionality.md)

---

## Test Data Requirements

### User Credentials
- Valid test users with unique usernames
- Invalid credentials for negative testing

### Image Files
- Valid image formats: JPG, PNG (various sizes)
- Invalid formats: TXT, EXE
- Large files: > 50MB
- Edge cases: 0 bytes, corrupted files

### Video Files
- Valid video formats: MP4, MOV, AVI
- Various lengths: 5s, 30s, 2min
- Different resolutions: 720p, 1080p, 4K

### Model Weights (Optional)
- `trufor.pth.tar` (~249MB)
- DeepfakeBench weights (~780MB total)

---

## Notes for Testers

1. **Environment Setup**: Tests assume Docker environment or local Python setup
2. **Test Independence**: Each test should be independent and not rely on others
3. **Cleanup**: Tests should clean up created data (test users, uploaded files)
4. **Documentation**: Update "Actual Result" and "Status" fields after test execution
5. **Evidence**: Capture screenshots/logs for failed tests

---

**Document Control**:
- **Version**: 2.0
- **Created**: October 25, 2025
- **Last Updated**: October 26, 2025
- **Author**: Xiyu Guan
- **Review Cycle**: After each test cycle
- **Latest Review**: Post Cycle 1 (Oct 26, 2025)

**Change Log**:
- **V1.0** (Oct 25): Initial test case documentation created
- **V2.0** (Oct 26): Updated with Cycle 1 execution results, added status quick reference

