# Deepfake Detection System V3 - Sequence Diagram

## System Interaction Flow

### 1. User Registration Sequence

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant AuthSvc as Authentication Service
    participant UserMgr as User Manager
    participant Storage as JSON Storage

    Note over User,Storage: New User Registration

    User->>WebUI: Access /web/register.html
    WebUI-->>User: Display Registration Form
    
    User->>WebUI: Enter username & password
    WebUI->>WebUI: Validate Input (client-side)
    WebUI->>FastAPI: POST /auth/register {username, password}
    
    FastAPI->>AuthSvc: register_user(username, password)
    AuthSvc->>UserMgr: check_user_exists(username)
    UserMgr->>Storage: Load users.json
    Storage-->>UserMgr: Existing users data
    
    alt Username Already Exists
        UserMgr-->>AuthSvc: User exists error
        AuthSvc-->>FastAPI: HTTPException(400, "Username already exists")
        FastAPI-->>WebUI: Error Response
        WebUI-->>User: Show Error Message
    else Username Available
        AuthSvc->>AuthSvc: hash_password(password)
        AuthSvc->>UserMgr: create_user(username, hashed_password)
        UserMgr->>Storage: Save to users.json
        Storage-->>UserMgr: Success
        UserMgr-->>AuthSvc: User created
        AuthSvc-->>FastAPI: {message: "User registered"}
        FastAPI-->>WebUI: Success Response
        WebUI-->>User: Redirect to Login Page
    end
```

### 2. User Login Sequence

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant AuthSvc as Authentication Service
    participant UserMgr as User Manager
    participant Storage as JSON Storage

    Note over User,Storage: User Authentication

    User->>WebUI: Access /web/login.html
    WebUI-->>User: Display Login Form
    
    User->>WebUI: Enter username & password
    WebUI->>FastAPI: POST /auth/login {username, password}
    
    FastAPI->>AuthSvc: authenticate_user(username, password)
    AuthSvc->>UserMgr: get_user(username)
    UserMgr->>Storage: Load users.json
    Storage-->>UserMgr: User data
    
    alt Invalid Credentials
        UserMgr-->>AuthSvc: User not found
        AuthSvc-->>FastAPI: HTTPException(401, "Invalid credentials")
        FastAPI-->>WebUI: Error Response
        WebUI-->>User: Show Error Message
    else Valid Credentials
        AuthSvc->>AuthSvc: verify_password(plain, hashed)
        alt Password Correct
            AuthSvc->>AuthSvc: create_access_token({sub: username})
            AuthSvc-->>FastAPI: {access_token, token_type: "bearer"}
            FastAPI-->>WebUI: JWT Token
            WebUI->>WebUI: Store token in localStorage
            WebUI-->>User: Redirect to Main Page
        else Password Incorrect
            AuthSvc-->>FastAPI: HTTPException(401, "Invalid credentials")
            FastAPI-->>WebUI: Error Response
            WebUI-->>User: Show Error Message
        end
    end
```

### 3. Image Detection with Authentication Sequence

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant AuthDec as Auth Decorator
    participant DetectSvc as Detection Service
    participant TruFor as TruFor Adapter
    participant HistMgr as History Manager
    participant Storage as Job Storage

    Note over User,Storage: Authenticated Image Detection

    User->>WebUI: Upload Image File
    WebUI->>WebUI: Get JWT Token from localStorage
    
    alt No Token
        WebUI->>WebUI: Show "Please login first"
        WebUI-->>User: Redirect to Login Page
    else Token Exists
        WebUI->>FastAPI: POST /detect (with Authorization: Bearer <token>)
        
        FastAPI->>AuthDec: get_current_user(token)
        AuthDec->>AuthDec: Decode JWT Token
        
        alt Token Invalid/Expired
            AuthDec-->>FastAPI: HTTPException(401, "Invalid token")
            FastAPI-->>WebUI: 401 Unauthorized
            WebUI->>WebUI: Remove token from localStorage
            WebUI-->>User: Redirect to Login Page
        else Token Valid
            AuthDec-->>FastAPI: User data {username}
            
            FastAPI->>DetectSvc: detect_image(file, user)
            
            DetectSvc->>HistMgr: create_job(user, filename, "image")
            HistMgr->>Storage: Save job metadata
            Storage-->>HistMgr: job_id
            
            DetectSvc->>DetectSvc: Validate file (type, size)
            DetectSvc->>TruFor: detect(file_bytes)
            
            TruFor->>TruFor: Preprocess image
            TruFor->>TruFor: Run inference
            TruFor->>TruFor: Generate heatmaps
            TruFor-->>DetectSvc: Detection results
            
            DetectSvc->>HistMgr: update_job_status(job_id, "completed", results)
            HistMgr->>Storage: Update job data
            
            DetectSvc-->>FastAPI: Detection response
            FastAPI-->>WebUI: Results JSON
            
            WebUI->>WebUI: Parse results
            WebUI->>WebUI: Display visualization
            WebUI-->>User: Show detection results
        end
    end
```

### 4. Video Detection with DeepfakeBench Sequence

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant AuthDec as Auth Decorator
    participant DetectSvc as Detection Service
    participant DFBench as DeepfakeBench Adapter
    participant Models as DeepfakeBench Models
    participant HistMgr as History Manager
    participant Storage as Job Storage

    Note over User,Storage: Multi-Model Video Analysis

    User->>WebUI: Upload Video & Select Models
    WebUI->>WebUI: Get JWT Token
    WebUI->>FastAPI: POST /api/deepfakebench/analyze<br/>(video, model_keys[], Authorization)
    
    FastAPI->>AuthDec: get_current_user(token)
    AuthDec-->>FastAPI: User data
    
    FastAPI->>DetectSvc: analyze_video(video, models, user)
    
    DetectSvc->>HistMgr: create_job(user, filename, "video")
    HistMgr->>Storage: Save job metadata
    Storage-->>HistMgr: job_id
    
    DetectSvc->>DFBench: analyze_video(video_file, model_keys)
    
    DFBench->>DFBench: Extract frames (FPS=3)
    DFBench->>DFBench: check_model_availability()
    
    loop For each selected model
        DFBench->>Models: Load model weights
        Models-->>DFBench: Model ready
        
        loop For each frame
            DFBench->>Models: Predict frame
            Models-->>DFBench: Frame score
        end
        
        DFBench->>DFBench: Aggregate frame scores
    end
    
    DFBench->>DFBench: Calculate ensemble prediction
    DFBench->>DFBench: Generate timeline segments
    DFBench->>DFBench: Extract keyframes
    DFBench-->>DetectSvc: Analysis results
    
    DetectSvc->>HistMgr: update_job_status(job_id, "completed", results)
    HistMgr->>Storage: Save complete results
    
    DetectSvc-->>FastAPI: Video analysis response
    FastAPI-->>WebUI: Results JSON
    
    WebUI->>WebUI: Display timeline
    WebUI->>WebUI: Show keyframes
    WebUI->>WebUI: Render model scores
    WebUI-->>User: Interactive results display
```

### 5. History Access and Report Generation Sequence

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant AuthDec as Auth Decorator
    participant HistMgr as History Manager
    participant ReportGen as Report Generator
    participant PDFGen as PDF Generator
    participant ZIPGen as ZIP Generator
    participant Storage as Job Storage

    Note over User,Storage: History Viewing and Report Download

    User->>WebUI: Access /web/history.html
    WebUI->>WebUI: Get JWT Token
    WebUI->>FastAPI: GET /history (Authorization: Bearer <token>)
    
    FastAPI->>AuthDec: get_current_user(token)
    AuthDec-->>FastAPI: User data
    
    FastAPI->>HistMgr: get_user_jobs(user, filters)
    HistMgr->>Storage: Query user's jobs
    Storage-->>HistMgr: Job records
    HistMgr-->>FastAPI: List of jobs
    FastAPI-->>WebUI: Jobs JSON
    
    alt Desktop View (width > 768px)
        WebUI->>WebUI: Render table layout
    else Mobile View (width ≤ 768px)
        WebUI->>WebUI: Render card layout
    end
    
    WebUI-->>User: Display history
    
    alt User Requests PDF Report
        User->>WebUI: Click "📄 PDF" button
        WebUI->>FastAPI: GET /download/pdf/{job_id} (Authorization)
        
        FastAPI->>AuthDec: Verify user owns job
        FastAPI->>ReportGen: generate_pdf(job_id)
        
        ReportGen->>HistMgr: get_job_details(job_id)
        HistMgr->>Storage: Load job data
        Storage-->>HistMgr: Complete job data
        
        ReportGen->>PDFGen: create_report(job_data)
        PDFGen->>PDFGen: Add header
        PDFGen->>PDFGen: Add detection results
        PDFGen->>PDFGen: Add visualizations
        PDFGen->>PDFGen: Add metadata
        PDFGen-->>ReportGen: PDF bytes
        
        ReportGen-->>FastAPI: PDF file
        FastAPI-->>WebUI: PDF download
        WebUI-->>User: Save report_<job_id>.pdf
    
    else User Requests ZIP Package
        User->>WebUI: Click "📦 ZIP" button
        WebUI->>FastAPI: GET /download/zip/{job_id} (Authorization)
        
        FastAPI->>AuthDec: Verify user owns job
        FastAPI->>ReportGen: generate_zip(job_id)
        
        ReportGen->>ZIPGen: create_archive(job_data)
        ZIPGen->>ZIPGen: Add PDF report
        ZIPGen->>ZIPGen: Add results JSON
        ZIPGen->>ZIPGen: Add visualizations
        ZIPGen->>ZIPGen: Add metadata.txt
        ZIPGen-->>ReportGen: ZIP bytes
        
        ReportGen-->>FastAPI: ZIP file
        FastAPI-->>WebUI: ZIP download
        WebUI-->>User: Save results_<job_id>.zip
    
    else User Deletes Job
        User->>WebUI: Click "🗑️ Delete" button
        WebUI->>FastAPI: DELETE /history/{job_id} (Authorization)
        
        FastAPI->>AuthDec: Verify user owns job
        FastAPI->>HistMgr: delete_job(job_id, user)
        HistMgr->>Storage: Remove job files
        HistMgr-->>FastAPI: Success
        FastAPI-->>WebUI: 200 OK
        WebUI->>WebUI: Remove job from display
        WebUI-->>User: Show success message
    end
```

### 6. Mobile Responsive Rendering Sequence

```mermaid
sequenceDiagram
    participant User
    participant Browser as Browser
    participant WebUI as Web Interface
    participant CSS as Responsive CSS
    participant JS as JavaScript

    Note over User,JS: Adaptive Layout Rendering

    User->>Browser: Access history page
    Browser->>WebUI: Load /web/history.html
    WebUI->>Browser: HTML content
    
    Browser->>CSS: Load stylesheets
    CSS->>CSS: Check viewport width
    
    alt Desktop (width > 768px)
        CSS->>CSS: Apply desktop styles
        CSS->>Browser: Show table layout
        Browser->>JS: Initialize table events
        JS->>JS: Setup sort/filter handlers
    else Mobile (width ≤ 768px)
        CSS->>CSS: Apply mobile styles
        CSS->>Browser: Show card layout
        Browser->>JS: Initialize card events
        JS->>JS: Setup touch handlers
    end
    
    Browser-->>User: Render appropriate layout
    
    alt User Resizes Window
        User->>Browser: Change window size
        Browser->>CSS: Trigger media query
        CSS->>CSS: Recalculate layout
        CSS->>Browser: Update styles
        Browser->>JS: Trigger resize event
        JS->>JS: Re-initialize handlers
        Browser-->>User: Update display
    end
```

### 7. CI/CD Pipeline Sequence

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Git as Git Repository
    participant GHA as GitHub Actions
    participant CI as CI Manager
    participant Docker as Docker Registry
    participant Notif as Notifications

    Note over Dev,Notif: Continuous Integration Flow

    Dev->>Git: git push origin main
    Git->>GHA: Trigger CI workflow
    
    GHA->>CI: Start CI pipeline
    
    CI->>CI: Checkout code
    CI->>CI: Setup Python environment
    
    par Code Quality Checks
        CI->>CI: Run flake8
        CI->>CI: Run black --check
        CI->>CI: Run isort --check
    and Security Scan
        CI->>CI: Run Trivy scan
        CI->>CI: Generate SARIF report
    and Unit Tests
        CI->>CI: Install dependencies
        CI->>CI: Run pytest
    and Docker Build
        CI->>CI: Build Docker image
        CI->>Docker: Push image (if main branch)
    and Config Validation
        CI->>CI: Validate YAML files
        CI->>CI: Validate JSON files
    end
    
    alt All Checks Pass
        CI-->>GHA: Success ✅
        GHA-->>Git: Update commit status
        GHA->>Notif: Success notification
        Notif-->>Dev: CI passed
    else Any Check Fails
        CI-->>GHA: Failure ❌
        GHA-->>Git: Update commit status
        GHA->>Notif: Failure notification
        Notif-->>Dev: CI failed (with logs)
    end
```

### 8. Token Expiration Handling Sequence

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant AuthDec as Auth Decorator
    participant UserMgr as User Manager

    Note over User,UserMgr: Token Lifecycle Management

    User->>WebUI: Perform action after 24 hours
    WebUI->>WebUI: Get stored JWT token
    WebUI->>FastAPI: API request with expired token
    
    FastAPI->>AuthDec: get_current_user(token)
    AuthDec->>AuthDec: Decode JWT token
    AuthDec->>AuthDec: Check expiration time
    
    alt Token Expired
        AuthDec-->>FastAPI: HTTPException(401, "Token expired")
        FastAPI-->>WebUI: 401 Unauthorized
        WebUI->>WebUI: localStorage.removeItem('access_token')
        WebUI->>WebUI: localStorage.removeItem('user')
        WebUI->>WebUI: Show "Session expired. Please login again"
        WebUI-->>User: Redirect to /web/login.html
    
    else Token Revoked
        AuthDec->>UserMgr: is_token_revoked(token)
        UserMgr-->>AuthDec: true
        AuthDec-->>FastAPI: HTTPException(401, "Token revoked")
        FastAPI-->>WebUI: 401 Unauthorized
        WebUI->>WebUI: Clear localStorage
        WebUI-->>User: Redirect to login
    
    else Token Valid
        AuthDec-->>FastAPI: User data
        FastAPI->>FastAPI: Process request
        FastAPI-->>WebUI: Success response
        WebUI-->>User: Display results
    end
```

## Key Sequence Patterns

### 1. **Authentication Flow**
- Every protected endpoint requires JWT token
- Token validation happens before business logic
- Expired/invalid tokens redirect to login
- User data attached to request context

### 2. **Job Lifecycle**
1. Create job → Pending status
2. Process detection → Processing status
3. Save results → Completed status
4. Generate reports → Available for download
5. Optional deletion → Remove from history

### 3. **Error Handling**
- HTTP 400: Bad request (validation errors)
- HTTP 401: Unauthorized (auth failures)
- HTTP 403: Forbidden (permission denied)
- HTTP 404: Not found (job doesn't exist)
- HTTP 500: Internal server error

### 4. **Responsive Design**
- CSS media queries detect viewport size
- JavaScript dynamically loads appropriate layout
- Touch events for mobile interactions
- Resize handlers for live adaptation

### 5. **Model Processing**
- TruFor: Single model, pixel-level analysis
- DeepfakeBench: Multi-model, frame-level analysis
- Results aggregation for ensemble predictions
- Timeline generation for video analysis

## Performance Optimizations

1. **Async Operations**: All I/O operations non-blocking
2. **Lazy Loading**: Models loaded only when needed
3. **Caching**: Model weights persist across requests
4. **Connection Pooling**: Efficient resource management
5. **Batch Processing**: Multiple frames processed together
6. **Progressive Rendering**: UI updates as results arrive

## Security Considerations

1. **Token Validation**: Every request verified
2. **User Isolation**: Jobs scoped to user
3. **Input Sanitization**: File validation before processing
4. **Rate Limiting**: Protection against abuse
5. **Secure Storage**: Passwords hashed with bcrypt
6. **CORS**: Controlled cross-origin access

---

**Document Version**: 3.0  
**Last Updated**: October 25, 2025  
**Author**: Xiyu Guan

