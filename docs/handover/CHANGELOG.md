# Changelog

All notable changes to the Deepfake Detection System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2025-11-05

### Added
- 🆕 **Model Directory Structure**
  - Created `models/.gitkeep` to track empty directory
  - Added `models/README.md` with download instructions and verification steps
  - Updated `.gitignore` to properly handle models directory

- 🆕 **Organized Documentation Structure**
  - Created `docs/guides/` directory for user guides and technical documentation
  - Created `docs/handover/` directory for project handover documents
  - Moved CI setup guide to `docs/testing/` for better organization
  - Streamlined documentation navigation and discoverability

### Changed
- 📦 **Model Path Restructure** (Breaking Change for Manual Installations)
  - Moved all model files to centralized `models/` directory
  - TruFor weights: `trufor.pth.tar` → `models/trufor.pth.tar`
  - DeepfakeBench: `vendors/DeepfakeBench/` → `models/vendors/DeepfakeBench/`
  - Updated all code references (19 files) to use new paths
  - Updated Docker configuration for new directory structure
  - Enhanced `WEIGHTS_DOWNLOAD_GUIDE.md` with clearer extraction instructions

- 📚 **Documentation Optimization**
  - Streamlined `README.md` (from 694 lines to 454 lines, -35%)
  - Consolidated model setup documentation (removed redundant `MODEL_SETUP.md`)
  - Improved `WEIGHTS_DOWNLOAD_GUIDE.md` with step-by-step instructions
  - Updated all cross-document links (6 files) to reflect new structure
  - Clarified that `vendors.zip` includes all 12 model weights (no separate downloads needed)

### Removed
- ❌ **CLI Documentation** (Web-Only Focus)
  - Removed `BATCH_PROCESSING_GUIDE.md` (CLI batch processing guide)
  - Removed `DeepfakeBench_QUICK_START.md` (CLI quick start)
  - Removed `FRAME_INFERENCE_SETUP.md` (CLI technical setup)
  - Kept `tools/README.md` for advanced CLI users
  - Project now focuses on Web interface documentation

- ❌ **Redundant Documentation**
  - Removed `docs/MODEL_SETUP.md` (merged into `WEIGHTS_DOWNLOAD_GUIDE.md`)

### Fixed
- 🐛 **Bug Fixes from Cycle 3 Testing** (10 critical issues resolved)
  - BUG-007: Browser crash with large images (>1MB) - Added canvas size limits
  - BUG-009: Corrupted files showing "NaN%" - Added null checks
  - BUG-010: Invalid tokens not redirecting - Added client-side validation
  - BUG-011: F12 DevTools layout corruption - Fixed table column styling
  - BUG-012: No registration link on login page - Added registration link
  - BUG-013: Inconsistent navigation bars - Unified navbar across all pages
  - BUG-014: History records unsorted - Fixed chronological sorting by timestamp
  - BUG-015: Mobile responsive issues - Fixed navbar, table overflow, content centering
  - BUG-016: DeepfakeBench model info modal not showing - Fixed DaisyUI `.modal` class conflict by renaming to `.custom-modal`
  - ENHANCEMENT-005: Weak password policy - Added uppercase, lowercase, digit requirements

- 🔧 **Configuration and Path Fixes**
  - Fixed incorrect DeepfakeBench path in `HANDOVER_DOCUMENT.md` environment variables
  - Updated `.gitignore` to correctly ignore `models/` directory instead of old `vendors/` path
  - Added Docker volume mount for `models/` directory to enable hot-reload during development

- 🔗 **Link and Reference Fixes**
  - Fixed invalid internal links in `HANDOVER_DOCUMENT.md`
  - Fixed `README.md` table of contents link to "License and Attribution"
  - Updated 20+ documentation cross-references for new file locations

- 🌐 **Code Quality**
  - Removed all Chinese comments from codebase
  - Standardized all documentation to English
  - Fixed inconsistent file paths across documentation

### Infrastructure
- 🔧 **CI/CD Improvements**
  - All CI checks passing (100% test coverage maintained)
  - Fixed missing imports in test files
  - Updated test password to meet new password policy requirements

### Documentation
- 📖 **Updated Guides**
  - `WEIGHTS_DOWNLOAD_GUIDE.md` v3.1 - Complete model setup with new paths
  - `HANDOVER_DOCUMENT.md` v3.1 - Updated with new structure and traceability matrices
  - `README.md` v3.1 - Streamlined with focus on Docker deployment
  - All test documentation updated with new paths

### Migration Notes
- ⚠️ **For Existing Users**: Manual installations need to reorganize model files:
  ```bash
  # Create models directory
  mkdir -p models
  
  # Move TruFor weights
  mv trufor.pth.tar models/
  
  # Move DeepfakeBench
  mv vendors models/
  ```
- ✅ **Docker Users**: Simply rebuild the image with `docker compose up -d --build`

---

## [3.0.0] - 2025-10-25

### Added
- 🔐 **Complete Authentication System**
  - JWT token-based authentication
  - User registration and login endpoints (`/auth/register`, `/auth/login`)
  - Protected API endpoints requiring authentication
  - Token expiration (24 hours) and renewal mechanism
  - Token revocation list for logout functionality
  - Password hashing with bcrypt for secure storage

- 📜 **Detection History Management**
  - Persistent storage of all detection jobs
  - User-specific history isolation
  - Job status tracking (pending, processing, completed, failed)
  - Filter detection history by status, date, and media type
  - Delete individual detection records
  - History API endpoints (`/history`, `/history/{job_id}`)

- 📄 **Report Generation**
  - PDF report generation with comprehensive analysis
  - ZIP package creation including all results and artifacts
  - Download endpoints (`/download/pdf/{job_id}`, `/download/zip/{job_id}`)
  - Automated report formatting with detection visualizations

- 🎬 **DeepfakeBench Integration (12 Models)**
  - Complete integration of 12 frame-level detection models (FFD removed from V2.0's 13 models):
    1. Xception
    2. MesoNet-4
    3. MesoNet-4 Inception
    4. F3Net
    5. EfficientNet-B4
    6. Capsule Net
    7. SRM
    8. RECCE
    9. SPSL
    10. UCF
    11. CNN-AUG
    12. CORE
  - Multi-model video analysis with ensemble predictions
  - Model availability checking before analysis
  - Dynamic model loading and management
  - Video analysis endpoint (`/api/deepfakebench/analyze`)
  - Timeline generation for suspicious segments
  - Keyframe extraction from detected segments

- 📱 **Mobile-Responsive Design**
  - Responsive history page with breakpoint at 768px
  - Desktop: Table-based layout for large screens
  - Mobile: Card-based layout for touch devices
  - Adaptive navigation with hamburger menu
  - Touch-optimized buttons and interactions
  - Fully responsive across all pages

- 🔄 **CI/CD Pipeline**
  - GitHub Actions workflows for automated testing
  - Code quality checks (flake8, black, isort)
  - Security vulnerability scanning with Trivy
  - Docker build validation
  - Configuration file validation (YAML/JSON)
  - Unit test execution with pytest
  - Automated status badges

- 📐 **V3 Architecture Documentation**
  - Complete V3 domain model diagram with all system components
  - V3 sequence diagrams covering all major user flows:
    - User registration and login
    - Authenticated image detection
    - Multi-model video analysis
    - History access and report generation
    - Mobile responsive rendering
    - CI/CD pipeline
    - Token expiration handling
  - Comprehensive architecture documentation

### Fixed
- 🐛 **Video Detection Authentication Bug**
  - Fixed frontend not sending authentication token to `/detect` endpoint
  - Added Authorization header with Bearer token to all API requests
  - Implemented proper 401 error handling and redirect to login

- 🐛 **DeepfakeBench Model Loading Issues**
  - Resolved `ModuleNotFoundError` for multiple missing dependencies
  - Added required packages to `requirements.txt`:
    - simplejson, fvcore, iopath, av (for SlowFast)
    - scikit-learn, albumentations, tensorboard, omegaconf (for FaceXRay)
    - efficientnet-pytorch, lmdb, pretrainedmodels, kornia
    - dlib (with cmake and build-essential for compilation)
    - imgaug, loralib, transformers, einops
  - Fixed numpy compatibility by pinning version to `<2.0.0`
  - Refactored model loading to use DeepfakeBench's DETECTOR registry
  - Added `Callable` import to type hints in `tools/build_dfbench_model.py`

- 🐛 **Mobile UI Issues**
  - Fixed history page display on mobile devices
  - Implemented responsive card layout for history entries
  - Adjusted button sizes for touch-friendly interactions
  - Fixed overflow issues on small screens

- 🐛 **Docker Build Problems**
  - Added `cmake` and `build-essential` to Dockerfile for dlib compilation
  - Updated system dependencies in Docker image
  - Fixed model weight file copying in Docker build

### Removed
- ❌ **FFD Model**: Removed from DeepfakeBench integration (13 → 12 models)

### Changed
- 🌐 **Code Internationalization**
  - Replaced all Chinese comments with English throughout codebase
  - Updated error messages to English in frontend JavaScript
  - Standardized code documentation language to English

- ⚙️ **Configuration Updates**
  - Updated `requirements.txt` with 30+ new dependencies
  - Added Docker Compose configuration for easier deployment
  - Updated `.gitignore` to explicitly ignore `vendors/` directory
  - Added `.dockerignore` for optimized Docker builds

- 🔧 **Code Quality Improvements**
  - Improved error handling across all endpoints
  - Enhanced logging for debugging and monitoring
  - Standardized API response formats
  - Better separation of concerns in adapter classes

- 📝 **Documentation Updates**
  - Updated README.md with V3 features and CI badges
  - Added comprehensive architecture diagrams for V3
  - Created CHANGELOG.md for version tracking
  - Updated all documentation to reflect authentication requirements
  - Corrected model count from 13 to accurate number

### Security
- 🔒 **Authentication & Authorization**
  - Implemented JWT token-based authentication
  - Password hashing with bcrypt
  - Token expiration and revocation mechanisms
  - Protected all detection endpoints
  - User session management

- 🔒 **Input Validation**
  - File type validation for uploads
  - File size limits enforcement
  - MIME type checking
  - SQL injection prevention (JSON-based storage)

## [2.0.0] - 2025-10-12

### Added
- TruFor model integration for pixel-level detection
- Enhanced UI with modal dialogs
- Visualization improvements (heatmaps, confidence maps)
- Noiseprint++ analysis integration
- Configuration management system
- Multi-model architecture support

### Fixed
- Modal positioning and display issues
- Result visualization rendering
- Image preprocessing pipeline

### Changed
- Improved user interface design
- Better error messages and handling
- Enhanced result presentation

## [1.0.0] - Initial Release

### Added
- Basic deepfake detection with ResNet models
- Web interface for file upload
- Simple detection result display
- Docker deployment support

---

## Legend

- 🔐 Security
- 📜 Features
- 📄 Documentation
- 🎬 Models
- 📱 UI/UX
- 🔄 CI/CD
- 🐛 Bug Fixes
- 🌐 Internationalization
- ⚙️ Configuration
- 🔧 Code Quality
- 🔒 Security
- 📐 Architecture

---

**Maintained by**: Xiyu Guan  
**Repository**: https://github.com/fsrconsulting/deepfake-detector

