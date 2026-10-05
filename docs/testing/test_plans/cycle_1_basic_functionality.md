# Test Plan - Cycle 1: Basic Functionality

**Project**: Deepfake Detector  
**Test Cycle**: Cycle 1  
**Focus**: Basic Functionality and Core Features  
**Start Date**: October 25, 2025  
**End Date**: October 26, 2025  
**Tester(s)**: Xiyu Guan  
**Environment**: Local (Windows) + CI (GitHub Actions/Ubuntu)  
**Status**: ✅ Complete

---

## 1. Test Cycle Overview

### 1.1 Objectives
- ✅ Verify core system setup and configuration
- ✅ Test user authentication flow (register/login)
- ✅ Validate API endpoints accessibility
- ✅ Confirm basic integration between components
- ✅ Ensure CI/CD pipeline runs successfully

### 1.2 Scope

#### In Scope:
- Module imports and configuration validation
- User registration and login functionality
- JWT token generation and validation
- Protected endpoint authentication
- Health check and web page accessibility
- Basic error handling (401/403 responses)

#### Out of Scope:
- Model inference functionality (Cycle 2)
- File upload and detection (Cycle 2)
- Performance testing (Cycle 3)
- Security testing (Cycle 3)
- Edge cases with special characters (Cycle 2)

### 1.3 Test Environment

**Local Testing Environment**:
- **OS**: Windows 10/11
- **Docker**: Docker Desktop (local development)
- **Python**: 3.11
- **Test Framework**: pytest 7.4.0+
- **Execution**: Manual trigger by developer
- **Coverage**: pytest-cov with HTML reports

**CI Testing Environment**:
- **Platform**: GitHub Actions
- **OS**: Ubuntu Latest (runner)
- **Python**: 3.11
- **Test Framework**: pytest 7.4.0+
- **Execution**: Automatic on push/PR
- **Additional**: flake8, black, isort, Trivy security scan

**Test Data**:
- Test user credentials (generated during tests)
- No model weights required for Cycle 1
- Sample configuration files (configs/config.yaml)

---

## 2. Selected Test Cases

**Total Automated Tests**: 67 test cases (implemented in pytest)

### 2.1 Unit Tests (57 test cases)

| Category | Test Count | Priority | Coverage |
|----------|------------|----------|----------|
| Module Imports | 3 | High | All core modules |
| Configuration Validation | 2 | High | YAML files |
| Auth Functions | 10 | High | Password hashing, JWT tokens |
| History Management | 16 | High | Data persistence, filtering |
| Model Adapters | 20 | High | Weight registry, model discovery |
| Adapter Integration | 6 | High | TruFor, DeepfakeBench |

**Test Files**:
- `tests/test_basic.py` - Module imports, config validation
- `tests/test_auth.py` - Authentication functionality
- `tests/test_history.py` - History manager operations
- `tests/test_adapters.py` - Model adapter functionality

**Rationale**: Comprehensive unit testing ensures each component works correctly in isolation before integration testing.

---

### 2.2 Integration Tests (10 test cases)

| Test Category | Test Count | Priority | Focus |
|--------------|------------|----------|-------|
| API Endpoints | 5 | High | Registration, login, status |
| Protected Routes | 3 | High | Authentication required |
| Error Handling | 2 | High | 401/403 responses |

**Test Files**:
- `tests/test_integration.py` - API endpoint integration

**Key Test Cases**:
- User registration flow
- User login and token generation
- Protected endpoint access control
- Model status endpoint
- History endpoint with pagination
- Invalid token handling

**Rationale**: Verify components work together correctly through API calls.

---

### 2.3 CI Pipeline Tests (8 jobs)

**CI-specific checks** (not part of pytest):
1. **Code Quality** - flake8, black, isort
2. **Security Scan** - Trivy vulnerability detection
3. **Quick Validation** - Syntax error detection
4. **Docker Build** - Image build verification
5. **Config Validation** - YAML file structure

**Rationale**: Ensure code quality, security, and build success before deployment.

---

## 3. Test Execution Strategy

### 3.1 Local Testing (Developer-Initiated)

**Purpose**: Fast feedback during development

**Environment**: Windows 10/11, Local Docker

**Execution Steps**:
```bash
# 1. Navigate to project directory
cd c:\Users\21402\Desktop\deepfake-detector

# 2. Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=xml

# 3. Run specific test categories
pytest tests/ -v -m unit           # Unit tests only
pytest tests/ -v -m integration    # Integration tests only

# 4. View coverage report
# Open htmlcov/index.html in browser
```

**Expected Outcome**:
- ✅ All 67 tests pass
- ✅ Code coverage ≥ 60%
- ⏱️ Execution time: ~12 seconds

**When to Run**:
- Before committing code
- After making changes to core modules
- When debugging test failures

---

### 3.2 CI Testing (Automatic)

**Purpose**: Comprehensive validation before deployment

**Environment**: GitHub Actions (Ubuntu Latest)

**Trigger Events**:
- Push to `main` branch
- Pull Request creation
- Manual workflow dispatch

**CI Pipeline Jobs** (run in parallel):
1. **Code Quality Check** (~28s)
   - flake8 (linting)
   - black (formatting)
   - isort (import sorting)

2. **Security Scan** (~45s)
   - Trivy vulnerability scan
   - SARIF report upload

3. **Quick Validation** (~15s)
   - Syntax error detection (F821, F823)

4. **Unit Tests** (~1m 12s)
   - All 67 pytest tests
   - Coverage report generation
   - Coverage: 70%

5. **Docker Build** (~1m 32s)
   - Multi-stage image build
   - Build success verification

6. **Config Validation** (~8s)
   - YAML file structure check

**Expected Outcome**:
- ✅ All 5 jobs pass
- ✅ 67 tests pass on Ubuntu
- ✅ No security vulnerabilities
- ✅ Docker image builds successfully
- ⏱️ Total pipeline time: ~3-4 minutes

**CI Results Location**:
- GitHub Actions: `https://github.com/xiyug/deepfake-detector/actions`
- Artifacts: Coverage reports, test logs

---

### 3.3 Manual Testing

**Location**: `tests/manual/` directory

**Scripts**:
- `api_testing.py` - Manual API endpoint verification
- `model_loading.py` - Manual model weight verification

**Note**: Manual tests are NOT run in CI or automated testing. They are for developer use when models are available.

---

### 3.4 Testing Workflow

**Developer Workflow**:
```
1. Write/modify code
2. Run local tests (pytest)           ← Fast feedback (~12s)
3. Fix any failures
4. Commit and push
5. CI runs automatically               ← Comprehensive validation (~4m)
6. Review CI results
7. Merge if all checks pass ✅
```

**Benefits**:
- 🚀 **Local**: Fast iteration, immediate feedback
- 🛡️ **CI**: Automated quality gates, cross-platform validation
- 📊 **Both**: Catch different types of issues early

---

## 4. Entry and Exit Criteria

### 4.1 Entry Criteria
- ✅ Code is committed to `main` branch
- ✅ Docker image builds successfully
- ✅ CI pipeline passes (GitHub Actions)
- ✅ Test environment is set up

### 4.2 Exit Criteria
- ✅ All high-priority test cases pass
- ✅ At least 90% of selected tests pass
- ✅ All critical bugs are fixed
- ✅ Test report is completed and reviewed
- ✅ Code coverage ≥ 60%

---

## 5. Test Schedule

| Date | Activity | Owner | Status | Notes |
|------|----------|-------|--------|-------|
| Oct 25 | Setup test environment | Xiyu Guan | ✅ Complete | Local + CI configured |
| Oct 25 | Run initial tests (local) | Xiyu Guan | ✅ Complete | 7 failed, 51 passed |
| Oct 25 | Run initial CI tests | GitHub Actions | ✅ Complete | 3 jobs failed |
| Oct 25-26 | Fix bugs (5 commits) | Xiyu Guan | ✅ Complete | All issues resolved |
| Oct 26 | Rerun tests (local) | Xiyu Guan | ✅ Complete | 67 passed, 0 failed |
| Oct 26 | Rerun CI tests | GitHub Actions | ✅ Complete | All 5 jobs passed |
| Oct 26 | Complete test report | Xiyu Guan | ✅ Complete | cycle_1_report.md |
| Oct 26 | Cycle 1 sign-off | Xiyu Guan | ✅ Complete | All criteria met |

**Actual Duration**: 2 days (Oct 25-26)  
**Planned Duration**: 3 days (Oct 25-27)  
**Efficiency**: Completed 1 day early ✅

---

## 6. Risks and Mitigation

| Risk | Impact | Probability | Status | Actual Outcome |
|------|--------|-------------|--------|----------------|
| Docker environment issues | High | Low | ✅ Mitigated | No Docker issues encountered |
| CI pipeline failures | Medium | Medium | ✅ Occurred | 3 CI jobs failed initially, all fixed |
| Missing dependencies | High | Low | ✅ Occurred | httpx missing, added to requirements.txt |
| API compatibility issues | Medium | Medium | ✅ Occurred | 404 errors, added compatibility aliases |
| Test environment setup | Medium | Low | ✅ Resolved | Local + CI configured successfully |

**Actual Risks Encountered**:

1. **CI Permission Errors** (Medium Impact)
   - Security scan failed due to missing `security-events: write` permission
   - **Resolution**: Added permission to `.github/workflows/ci.yml`
   - **Time to Fix**: 1 hour

2. **Missing Test Dependencies** (High Impact)
   - httpx package required by TestClient not in requirements.txt
   - **Resolution**: Added httpx and pytest plugins to requirements.txt
   - **Time to Fix**: 30 minutes

3. **Import Errors in Tests** (High Impact)
   - Auth helper functions not accessible for import
   - **Resolution**: Refactored user_manager.py to expose functions
   - **Time to Fix**: 1 hour

4. **API Endpoint 404 Errors** (Medium Impact)
   - Tests expecting `/register` and `/token` endpoints
   - **Resolution**: Added compatibility aliases in main.py
   - **Time to Fix**: 45 minutes

**Mitigation Effectiveness**: ✅ All risks resolved within 1-2 hours each

---

## 7. Test Deliverables

**All deliverables completed** ✅

1. **Test Execution Logs**
   - Local: pytest terminal output
   - CI: GitHub Actions logs
   - Location: GitHub Actions artifacts

2. **Code Coverage Reports**
   - Local HTML: `htmlcov/index.html` (70% coverage)
   - CI XML: `coverage.xml` (uploaded as artifact)
   - Coverage badge: Can be integrated if needed

3. **Test Report Document**
   - Location: `docs/testing/test_reports/cycle_1_report.md`
   - Status: ✅ Complete (843 lines)
   - Contents: Executive summary, detailed results, evidence, defects, metrics

4. **Bug Reports**
   - 6 bugs identified and documented in test report
   - All bugs fixed and verified
   - Root cause analysis included

5. **CI/CD Pipeline Evidence**
   - Initial run: #142 (3 jobs failed)
   - Final run: #148 (all jobs passed)
   - Location: https://github.com/xiyug/deepfake-detector/actions

6. **Additional Deliverables**
   - Updated test files: 5 test modules
   - CI configuration: `.github/workflows/ci.yml`
   - Test configuration: `pytest.ini`
   - Manual test scripts: `tests/manual/`

---

## 8. Test Case Summary

**Total Executed**: 67 automated test cases

**By Type**:
- **Unit Tests**: 57 test cases (85%)
- **Integration Tests**: 10 test cases (15%)
- **CI Pipeline Jobs**: 5 jobs (quality, security, build)

**By Category**:
- Authentication: 10 tests ✅
- History Management: 16 tests ✅
- Model Adapters: 26 tests ✅
- API Endpoints: 10 tests ✅
- Configuration: 5 tests ✅

**By Automation**:
- Automated (pytest): 67 test cases (100%)
- Manual scripts: 2 scripts (not run in CI)

**Test Results**:
```
Initial Run:  7 failed, 51 passed, 2 skipped (76% pass rate)
Final Run:    0 failed, 67 passed, 2 skipped (100% pass rate)
```

**Code Coverage**:
- **Target**: ≥ 60%
- **Achieved**: 70%
- **Status**: ✅ Exceeded target by 10%

---

## 9. Approvals

| Role | Name | Date | Signature | Status |
|------|------|------|-----------|--------|
| Test Lead | Xiyu Guan | Oct 26, 2025 | _Approved_ | ✅ Complete |
| Developer | Xiyu Guan | Oct 26, 2025 | _Approved_ | ✅ Complete |
| Project Owner | Xiyu Guan | Oct 26, 2025 | _Approved_ | ✅ Complete |

---

## 10. Notes and Comments

**Key Achievements**:
- ✅ First test cycle completed successfully
- ✅ All 67 automated tests passing (100% pass rate)
- ✅ 70% code coverage achieved (exceeded 60% target)
- ✅ Cross-platform validation (Windows local + Ubuntu CI)
- ✅ Comprehensive CI pipeline established (5 jobs)

**Bugs Found and Fixed**:
- 6 bugs identified during testing
- All bugs fixed within test cycle (1-2 days)
- No critical or blocking issues remaining

**Testing Infrastructure**:
- Local testing: Fast iteration (~12 seconds)
- CI testing: Comprehensive validation (~4 minutes)
- Both environments show consistent results

**Next Steps**:
- Cycle 2 will focus on model inference and detection functionality
- Will require model weights for TruFor and DeepfakeBench
- Will add end-to-end testing with actual images/videos

**Lessons Learned**:
- Dual testing (local + CI) caught different types of issues
- Quick iteration on local tests accelerated bug fixing
- CI provided automated quality gates before deployment

---

**Document Version**: 2.0  
**Created**: October 25, 2025  
**Last Updated**: October 26, 2025  
**Status**: ✅ Complete  
**Next Cycle**: Cycle 2 - End-to-End Detection Testing

