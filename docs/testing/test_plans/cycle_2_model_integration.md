# Test Plan - Cycle 2: Model Integration

**Project**: Deepfake Detector  
**Test Cycle**: Cycle 2  
**Focus**: Model Loading and End-to-End Detection  
**Start Date**: October 26, 2025  
**End Date**: October 26, 2025 (Same Day - Fast Track)  
**Tester(s)**: Xiyu Guan  
**Environment**: Local (Windows) - Manual Testing Only  
**Status**: 🟡 In Progress

---

## 1. Test Cycle Overview

### 1.1 Objectives (Fast Track - Core Tests Only)
- ✅ Verify DeepfakeBench video analysis works
- ✅ Test file upload error handling (invalid files)
- ✅ Test large file upload handling
- ✅ Verify user registration validation
- ✅ Verify detection results stored in history
- ✅ Test report generation (PDF/ZIP)

**Note**: This is a **fast-track testing cycle** (2-3 hours) focusing on core functionality only. Comprehensive testing deferred to future cycles.

### 1.2 Scope (Fast Track)

#### In Scope (Core Tests Only - 6 tests):
1. ✅ Video analysis with DeepfakeBench (1 model test)
2. ✅ Invalid file format rejection
3. ✅ Large file upload handling
4. ✅ Duplicate username validation
5. ✅ History record verification
6. ✅ Report generation (PDF/ZIP)

#### Out of Scope (Deferred):
- ❌ TruFor image detection (skipped due to browser crash bug)
- ❌ Multiple model comparison
- ❌ Different image/video formats
- ❌ Performance benchmarking
- ❌ Concurrent requests testing
- ❌ Security testing (XSS, injection)
- ❌ Cross-browser compatibility
- ❌ API endpoint verification (endpoint not available)

### 1.3 Entry Criteria

**Prerequisites**:
- ✅ Cycle 1 completed with 100% pass rate
- ⚠️ Model weights downloaded and placed correctly:
  - `models/trufor.pth.tar` exists
  - `models/vendors/DeepfakeBench/training/weights/*.pth` present
- ⚠️ Test data prepared (sample images and videos)
- ✅ Docker environment working
- ✅ All Cycle 1 bugs fixed

### 1.4 Exit Criteria

- ✅ All high-priority test cases pass (≥90%)
- ✅ At least one successful TruFor detection
- ✅ At least one successful DeepfakeBench video analysis
- ✅ File upload works for valid formats
- ✅ Invalid files are rejected gracefully
- ✅ Detection results saved to history
- ✅ Code coverage ≥ 60% (including new code)

---

## 2. Test Environment

**Local Testing Environment**:
- **OS**: Windows 10/11
- **Docker**: Docker Desktop with model weights
- **Python**: 3.11
- **Test Framework**: pytest + manual testing
- **Model Weights**: TruFor (~249MB) + DeepfakeBench (~780MB)

**CI Testing Environment**:
- **Note**: CI tests will skip model inference tests (too large for CI)
- **Focus**: Unit tests for model loading logic only
- **Mock**: Use mock objects for actual inference

---

## 3. Selected Test Cases (Fast Track - 6 Core Tests)

### 3.1 Core Test Suite

| # | Test ID | Test Name | Priority | Time | Method |
|---|---------|-----------|----------|------|--------|
| 1 | TC-P-002 | DeepfakeBench Video Analysis | High | 30min | Manual |
| 2 | TC-E-103 | Invalid File Format Upload | High | 10min | Manual |
| 3 | TC-E-102 | Large File Upload Handling | High | 15min | Manual |
| 4 | TC-A-002 | Duplicate Username Registration | Medium | 5min | Manual |
| 5 | TC-I-012 | Detection Result in History | High | 10min | Manual |
| 6 | TC-I-013/014 | Report Generation (PDF/ZIP) | Medium | 20min | Manual |

**Total Estimated Time**: 1.5 hours (testing) + 0.5 hours (documentation) = **2 hours**

---

### 3.2 Deferred Tests (Not in This Cycle)

**Model Loading Tests** (Skipped - API not available):
- ⏭️ TC-M-001: TruFor Model Loading
- ⏭️ TC-M-004: DeepfakeBench Model Building

**Image Detection Tests** (Skipped - Browser crash bug):
- ⏭️ TC-P-001: TruFor Image Detection
- ⏭️ TC-D-001-006: All TruFor tests

**Additional Tests** (Time constraints):
- ⏭️ TC-V-002-006: Multiple model tests
- ⏭️ TC-E-104: Special characters
- ⏭️ TC-E-101: Concurrent requests
- ⏭️ TC-E-105-106: Security tests
- ⏭️ All performance benchmarks

---

## 4. Test Execution Strategy (Fast Track - Same Day)

### 4.1 Execution Timeline (2 Hours Total)

**18:00 - 18:30** (30 min) - Test 1: Video Analysis
- Upload test video (5-10s MP4)
- Select Xception model
- Measure analysis time
- Verify results displayed

**18:30 - 18:40** (10 min) - Test 2: Invalid File Upload
- Try uploading TXT file
- Verify rejection message
- Test with other invalid formats

**18:40 - 18:55** (15 min) - Test 3: Large File Upload
- Upload large video (>20MB)
- Check size limit handling
- Measure processing time if accepted

**18:55 - 19:00** (5 min) - Test 4: Duplicate Username
- Attempt duplicate registration
- Verify error handling

**19:00 - 19:10** (10 min) - Test 5: History Verification
- Check all detection records
- Verify data persistence
- Check filtering/sorting

**19:10 - 19:30** (20 min) - Test 6: Report Generation
- Generate PDF report
- Download ZIP package
- Verify file contents

**19:30 - 20:00** (30 min) - Documentation
- Update test report with results
- Organize screenshots
- Write summary

---

### 4.2 Testing Approach

**Single Pass Testing**:
- Execute each test once
- Record immediate results
- Move to next test quickly
- Document issues as found

**No Retries** (unless critical failure):
- If test fails, document and move on
- Focus on coverage, not perfection
- Time-boxed execution

**Evidence Collection**:
- Screenshot key results
- Copy-paste error messages
- Note timestamps

---

## 5. Test Schedule (Fast Track - Same Day)

| Time | Test | Owner | Status |
|------|------|-------|--------|
| 18:00-18:30 | Video Analysis | Xiyu Guan | 🟡 In Progress |
| 18:30-18:40 | Invalid File Upload | Xiyu Guan | 🟡 Pending |
| 18:40-18:55 | Large File Upload | Xiyu Guan | 🟡 Pending |
| 18:55-19:00 | Duplicate Username | Xiyu Guan | 🟡 Pending |
| 19:00-19:10 | History Verification | Xiyu Guan | 🟡 Pending |
| 19:10-19:30 | Report Generation | Xiyu Guan | 🟡 Pending |
| 19:30-20:00 | Documentation | Xiyu Guan | 🟡 Pending |

**Total Duration**: 2 hours  
**Target Completion**: October 26, 2025 20:00

---

## 6. Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Model weights too large for Git | High | High | Use .gitignore, document download process |
| Model loading fails in Docker | High | Medium | Test locally first, check Docker logs |
| Detection takes too long | Medium | Medium | Set reasonable timeouts, optimize if needed |
| Out of memory errors | High | Low | Monitor Docker memory, increase if needed |
| CI cannot test with models | Medium | High | Use mocked tests in CI, real tests locally |

---

## 7. Test Deliverables (Fast Track)

1. ✅ Test report document (cycle_2_report.md) - Updated in real-time
2. ✅ Screenshots of test execution (6 core tests)
3. ✅ Bug reports for issues found (BUG-007 already documented)
4. ✅ Test summary with pass/fail status
5. ⏭️ Performance metrics (basic timing only)
6. ⏭️ Detailed evidence (limited due to time constraints)

---

## 8. Success Criteria (Fast Track)

**Minimum Requirements** (Must Pass):
- ✅ At least 1 successful DeepfakeBench video analysis
- ✅ Invalid files rejected with clear errors
- ✅ System handles large files gracefully
- ✅ User validation works (duplicate check)
- ✅ Detection results saved to history
- ✅ 6 core tests completed and documented

**Success Metrics**:
- Pass Rate: ≥ 66% (4 out of 6 tests)
- Critical Bugs: ≤ 2
- Documented: All tests recorded in report

**Acceptable Outcomes**:
- Some tests may fail due to known bugs (BUG-007)
- Focus on coverage, not perfection
- Document issues for future fixes

---

## 9. Notes

- **Fast Track Mode**: Compressed 5-day plan into 2-hour execution
- **Model Weights**: Already available (Docker running)
- **Known Issues**: TruFor image detection crashes browser (BUG-007)
- **API Limitations**: `/api/models/status` endpoint not available (BUG-008)
- **Manual Testing**: 100% manual testing, no automation
- **Time Constraint**: Single-pass testing, minimal retries
- **Evidence**: Screenshots and basic metrics only

**Deferred to Future Cycles**:
- Comprehensive model testing
- Performance benchmarking
- Multiple format testing
- Security testing
- Cross-browser testing

---

**Document Version**: 2.0 (Fast Track Edition)  
**Created**: October 26, 2025  
**Last Updated**: October 26, 2025 18:00  
**Status**: 🟡 In Progress  
**Target Completion**: October 26, 2025 20:00  
**Prerequisites**: Cycle 1 Complete ✅


