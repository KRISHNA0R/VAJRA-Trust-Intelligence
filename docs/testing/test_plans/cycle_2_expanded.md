# Test Plan - Cycle 2 Expanded: Comprehensive Model & Integration Testing

**Project**: Deepfake Detector  
**Test Cycle**: Cycle 2 (Expanded)  
**Version**: 2.0  
**Last Updated**: October 26, 2025  
**Status**: 📋 Planned

---

## 1. Executive Summary

### 1.1 Objectives
This expanded Cycle 2 focuses on **comprehensive testing** of all model integration, detection workflows, edge cases, and user interactions.

**Test Scope**:
- ✅ Complete model integration testing (TruFor + DeepfakeBench)
- ✅ Full detection workflow (image + video)
- ✅ Edge cases and error handling
- ✅ User management and authentication edge cases
- ✅ File handling (valid, invalid, large, edge cases)
- ✅ History and reporting features
- ✅ Performance and security basics

**Out of Scope**:
- Heavy load testing (Cycle 3)
- Penetration testing (Cycle 3)
- UI/UX detailed testing (Cycle 3)

---

## 2. Test Categories & Cases

### 2.1 Model Integration Tests (6 tests)
| ID | Test Name | Priority | Est. Time | Type |
|----|-----------|----------|-----------|------|
| TC-M-001 | TruFor Model API Status | High | 10 min | Manual |
| TC-M-004 | DeepfakeBench Model API Status | High | 10 min | Manual |
| TC-P-001 | TruFor Image Detection | High | 20 min | Manual |
| TC-P-002 | DeepfakeBench Video Detection | High | 20 min | Manual |
| TC-P-003 | Multiple Model Comparison | Medium | 30 min | Manual |
| TC-P-004 | Model Performance Metrics | Medium | 20 min | Manual |

**Total**: ~1.5 hours

---

### 2.2 Detection Workflow Tests (8 tests)
| ID | Test Name | Priority | Est. Time | Type |
|----|-----------|----------|-----------|------|
| TC-D-001 | Image Detection - Valid JPG | High | 15 min | Manual |
| TC-D-002 | Image Detection - Valid PNG | High | 15 min | Manual |
| TC-D-003 | Image Detection - Multiple Sizes | Medium | 20 min | Manual |
| TC-D-004 | Video Detection - Valid MP4 | High | 15 min | Manual |
| TC-D-005 | Video Detection - Valid WEBM | Medium | 15 min | Manual |
| TC-D-006 | Video Detection - Various Lengths | Medium | 30 min | Manual |
| TC-D-007 | Detection Result Accuracy | High | 20 min | Manual |
| TC-D-008 | Detection Progress Feedback | Medium | 15 min | Manual |

**Total**: ~2.5 hours

---

### 2.3 Edge Cases & Error Handling (10 tests)
| ID | Test Name | Priority | Est. Time | Type |
|----|-----------|----------|-----------|------|
| TC-E-003 | Detection - No File Provided | High | 10 min | Manual |
| TC-E-101 | Concurrent Detection Requests | Medium | 20 min | Manual |
| TC-E-102 | Large File Upload (>50MB) | Medium | 15 min | Manual |
| TC-E-103 | Invalid File Format (.txt, .exe) | High | 15 min | ✅ Done |
| TC-E-104 | Special Characters in Inputs | Medium | 15 min | Manual |
| TC-E-105 | Empty Request Body | Medium | 10 min | Manual |
| TC-E-106 | SQL Injection Attempt | High | 15 min | Manual |
| TC-E-107 | Corrupted Image File | Medium | 15 min | Manual |
| TC-E-108 | Zero-byte File Upload | Low | 10 min | Manual |
| TC-E-109 | File Size Limit Boundary | Low | 15 min | Manual |

**Total**: ~2.5 hours (TC-E-103 already done)

---

### 2.4 User Management Tests (5 tests)
| ID | Test Name | Priority | Est. Time | Type |
|----|-----------|----------|-----------|------|
| TC-A-002 | Duplicate Username Registration | High | 10 min | Manual |
| TC-A-008 | Password Strength Validation | Medium | 15 min | Manual |
| TC-A-009 | Multiple Login Sessions | Medium | 15 min | Manual |
| TC-A-010 | Token Expiry Handling | High | 20 min | Manual |
| TC-A-011 | Logout and Token Revocation | Medium | 15 min | Manual |

**Total**: ~1.5 hours

---

### 2.5 History & Reporting Tests (6 tests)
| ID | Test Name | Priority | Est. Time | Type |
|----|-----------|----------|-----------|------|
| TC-I-012 | History Record Creation | High | 10 min | ✅ Done |
| TC-I-013 | PDF Report Generation | High | 10 min | ✅ Done |
| TC-I-014 | ZIP Report Generation | Medium | 15 min | Manual |
| TC-I-015 | History Pagination | Medium | 15 min | Manual |
| TC-I-016 | History Filtering | Medium | 15 min | Manual |
| TC-I-017 | Delete Detection Record | Medium | 10 min | Manual |

**Total**: ~1 hour (2 tests already done)

---

### 2.6 Performance Tests (4 tests)
| ID | Test Name | Priority | Est. Time | Type |
|----|-----------|----------|-----------|------|
| TC-P-010 | Image Detection Response Time | Medium | 20 min | Manual |
| TC-P-011 | Video Analysis Speed | Medium | 20 min | ✅ Done |
| TC-P-012 | API Endpoint Response Times | Medium | 20 min | Manual |
| TC-P-013 | Memory Usage During Detection | Low | 30 min | Manual |

**Total**: ~1 hour (TC-P-011 already done)

---

### 2.7 Integration & Workflow Tests (4 tests)
| ID | Test Name | Priority | Est. Time | Type |
|----|-----------|----------|-----------|------|
| TC-W-001 | Complete Detection Workflow | High | 30 min | Manual |
| TC-W-002 | Multi-User Scenario | Medium | 30 min | Manual |
| TC-W-003 | Cross-Page Navigation | Medium | 20 min | Manual |
| TC-W-004 | Mobile Responsiveness | Medium | 30 min | Manual |

**Total**: ~2 hours

---

## 3. Test Summary

### 3.1 Total Test Count
| Category | Tests | Already Done | Remaining | Est. Time |
|----------|-------|--------------|-----------|-----------|
| Model Integration | 6 | 2 (partial) | 4 | 1.5 hours |
| Detection Workflow | 8 | 0 | 8 | 2.5 hours |
| Edge Cases | 10 | 1 | 9 | 2.5 hours |
| User Management | 5 | 0 | 5 | 1.5 hours |
| History & Reporting | 6 | 2 | 4 | 1 hour |
| Performance | 4 | 1 | 3 | 1 hour |
| Integration | 4 | 0 | 4 | 2 hours |
| **TOTAL** | **43** | **6** | **37** | **~12 hours** |

### 3.2 Fast Track vs Expanded
- **Fast Track (Done)**: 6 tests, 2 hours, 80% pass rate
- **Expanded (Proposed)**: 43 tests, ~12-15 hours, comprehensive coverage

---

## 4. Recommended Execution Strategy

### 4.1 Option 1: Full Comprehensive (2-3 days)
Execute all 43 tests systematically for maximum coverage.

**Timeline**:
- Day 1: Model Integration + Detection Workflow (4 hours)
- Day 2: Edge Cases + User Management (4 hours)
- Day 3: History/Reporting + Performance + Integration (4 hours)

### 4.2 Option 2: Prioritized Medium (1 day)
Focus on High priority tests only (25 tests, ~6-7 hours).

**Include**:
- All model integration tests
- Core detection workflows
- Critical edge cases (invalid files, no file, SQL injection)
- User management (duplicate, token expiry)
- History & PDF report
- Complete workflow test

### 4.3 Option 3: Extended Fast Track (4-5 hours)
Add 10-12 most important tests to existing Fast Track.

**Add to Fast Track**:
1. TC-E-003: No file provided
2. TC-E-107: Corrupted file
3. TC-A-002: Duplicate username
4. TC-A-010: Token expiry
5. TC-D-001: JPG detection
6. TC-D-002: PNG detection
7. TC-D-004: MP4 video
8. TC-I-014: ZIP report
9. TC-I-017: Delete record
10. TC-W-001: Complete workflow
11. TC-E-106: SQL injection
12. TC-P-010: Response times

**New Total**: 18 tests, ~6-7 hours, 85%+ coverage

---

## 5. Detailed Test Cases

### 5.1 High Priority New Tests

#### TC-E-003: Detection - No File Provided
**Objective**: Verify error handling when no file is uploaded

**Steps**:
1. Navigate to Image Detection page
2. Click "Detect" without selecting file
3. Verify error message displayed
4. Navigate to Video Analysis page
5. Click "Analyze" without selecting file
6. Verify error message displayed

**Expected**: Clear error: "Please select a file"

**Priority**: High | Time: 10 min

---

#### TC-A-002: Duplicate Username Registration
**Objective**: Verify system rejects duplicate usernames

**Steps**:
1. Register user "test_duplicate_001"
2. Logout
3. Try to register same username again
4. Verify error message

**Expected**: Error: "Username already exists"

**Priority**: High | Time: 10 min

---

#### TC-E-106: SQL Injection Attempt
**Objective**: Verify SQL injection protection

**Steps**:
1. Try to register with username: `admin' OR '1'='1`
2. Try to login with username: `' OR '1'='1' --`
3. Verify requests are sanitized/rejected

**Expected**: No SQL injection possible

**Priority**: High | Time: 15 min

---

#### TC-D-001: Image Detection - Valid JPG
**Objective**: Test JPG image detection

**Steps**:
1. Upload valid JPG image (different from previous tests)
2. Verify detection completes
3. Check results display correctly
4. Verify saved to history

**Expected**: Detection works for JPG

**Priority**: High | Time: 15 min

---

#### TC-D-004: Video Detection - Valid MP4
**Objective**: Test MP4 video detection with different model

**Steps**:
1. Upload valid MP4 video
2. Select different model (e.g., MesoNet)
3. Analyze video
4. Verify results

**Expected**: Different models produce results

**Priority**: High | Time: 15 min

---

#### TC-I-014: ZIP Report Generation
**Objective**: Verify ZIP archive generation

**Steps**:
1. Complete detection
2. Navigate to History
3. Click "ZIP" button
4. Verify ZIP downloads
5. Extract and check contents

**Expected**: ZIP contains all artifacts

**Priority**: Medium | Time: 15 min

---

#### TC-W-001: Complete Detection Workflow
**Objective**: Test entire user journey

**Steps**:
1. Register new user
2. Login
3. Upload and detect image
4. Upload and analyze video
5. Check history (2 records)
6. Generate PDF for each
7. Generate ZIP for one
8. Delete one record
9. Logout

**Expected**: All steps work smoothly

**Priority**: High | Time: 30 min

---

#### TC-E-107: Corrupted Image File
**Objective**: Test handling of corrupted files

**Steps**:
1. Create corrupted image file:
   - Rename .txt to .jpg
   - Or truncate valid .jpg file
2. Upload to Image Detection
3. Verify graceful error handling

**Expected**: Error message, no crash

**Priority**: Medium | Time: 15 min

---

#### TC-A-010: Token Expiry Handling
**Objective**: Verify token expiration works

**Steps**:
1. Login and get token
2. Wait for token to expire (or modify code for quick test)
3. Try to access protected endpoint
4. Verify 401 response
5. Verify redirect to login page

**Expected**: Expired token rejected

**Priority**: High | Time: 20 min

---

## 6. Test Data Requirements

### 6.1 Images
- Small JPG (< 1MB) ✅
- Large JPG (> 5MB)
- PNG file (various sizes)
- HEIC/HEIF file
- Corrupted JPG
- Renamed TXT → JPG

### 6.2 Videos
- Short MP4 (< 10 sec) ✅
- Long MP4 (> 1 min)
- WEBM file
- AVI file
- Corrupted MP4

### 6.3 Invalid Files
- .txt file ✅
- .exe file
- .zip file
- Zero-byte file
- 50MB+ file

---

## 7. Success Criteria

### 7.1 Minimum (Pass)
- ✅ 30+ tests executed (70%)
- ✅ 80%+ pass rate
- ✅ All critical bugs documented
- ✅ No unresolved high-severity bugs

### 7.2 Target (Good)
- ✅ 37+ tests executed (85%)
- ✅ 85%+ pass rate
- ✅ All edge cases covered
- ✅ Performance benchmarks established

### 7.3 Excellent
- ✅ All 43 tests executed (100%)
- ✅ 90%+ pass rate
- ✅ Complete documentation
- ✅ Automated test expansion plan

---

## 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Time constraint | High | High | Use Option 3 (Extended Fast Track) |
| Missing test data | Medium | Medium | Prepare test data in advance |
| Model weights missing | Low | High | Already verified working |
| Environment issues | Low | Medium | Use Docker (stable) |
| Browser compatibility | Medium | Low | Stick to Chrome for Cycle 2 |

---

## 9. Deliverables

1. ✅ Expanded test report (`cycle_2_expanded_report.md`)
2. ✅ Test evidence (screenshots, logs, artifacts)
3. ✅ Bug reports (if any new bugs found)
4. ✅ Performance benchmarks
5. ✅ Coverage analysis
6. ✅ Recommendations for Cycle 3

---

## 10. Next Steps

### 10.1 Immediate (Now)
1. Review this expanded plan with team
2. Choose execution strategy (Option 1, 2, or 3)
3. Prepare test data
4. Set up test environment

### 10.2 Execution (Next)
1. Execute tests according to chosen option
2. Document results in real-time
3. Report bugs immediately
4. Update test evidence directory

### 10.3 Completion
1. Finalize test report
2. Calculate final metrics
3. Sign off on Cycle 2
4. Plan Cycle 3 (if needed)

---

**Plan Version**: 1.0 (Expanded)  
**Author**: Xiyu Guan  
**Date**: October 26, 2025  
**Estimated Total Time**: 12-15 hours (full) | 6-7 hours (prioritized) | 4-5 hours (extended fast track)



