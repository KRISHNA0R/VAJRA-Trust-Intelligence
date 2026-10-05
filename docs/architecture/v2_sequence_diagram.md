# Deepfake Detection System V2 - Sequence Diagram

## System Interaction Flow

### 1. Application Startup Sequence

```mermaid
sequenceDiagram
    participant User
    participant FastAPI as FastAPI Application
    participant Config as Configuration Manager
    participant ModelMgr as Model Manager
    participant TruFor as TruFor Adapter
    participant ResNet as ResNet Adapter
    participant WebUI as Web Interface

    Note over User,WebUI: System Initialization

    User->>FastAPI: Start Application
    FastAPI->>Config: Load Configuration
    Config-->>FastAPI: Return Config (model_type, paths, settings)
    
    FastAPI->>ModelMgr: Initialize Model Manager
    ModelMgr->>ModelMgr: Validate Model Files
    
    alt TruFor Model Selected
        ModelMgr->>TruFor: Initialize TruFor Adapter
        TruFor->>TruFor: Setup Device (CPU/GPU)
        TruFor->>TruFor: Load Model Weights
        TruFor->>TruFor: Load Configuration
        TruFor-->>ModelMgr: Adapter Ready
    else ResNet Model Selected
        ModelMgr->>ResNet: Initialize ResNet Adapter
        ResNet->>ResNet: Setup Device (CPU/GPU)
        ResNet->>ResNet: Load Model Weights
        ResNet->>ResNet: Setup Transforms
        ResNet-->>ModelMgr: Adapter Ready
    end
    
    ModelMgr-->>FastAPI: Model Initialized
    FastAPI->>FastAPI: Mount Static Files
    FastAPI->>FastAPI: Configure CORS
    FastAPI->>FastAPI: Setup Middleware
    FastAPI-->>User: Server Ready (http://localhost:8000)
    
    User->>WebUI: Access Web Interface
    WebUI-->>User: Display Upload Interface
```

### 2. Image Detection Sequence (TruFor Model)

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant DetectionSvc as Detection Service
    participant TruFor as TruFor Adapter
    participant Model as TruFor Model
    participant Processor as Media Processor
    participant Modal as Decision Modal

    Note over User,Modal: Image Upload and Analysis

    User->>WebUI: Select Image File
    WebUI->>WebUI: Validate File Type/Size
    WebUI->>FastAPI: POST /detect (multipart/form-data)
    
    FastAPI->>DetectionSvc: Process Upload Request
    DetectionSvc->>DetectionSvc: Validate MIME Type
    DetectionSvc->>DetectionSvc: Validate File Size (<10MB)
    DetectionSvc->>DetectionSvc: Read File Content
    
    DetectionSvc->>TruFor: detect(file_bytes, filename, mime_type)
    
    TruFor->>Processor: Preprocess Image
    Processor->>Processor: Convert to PIL Image
    Processor->>Processor: Apply Transforms (resize, normalize)
    Processor-->>TruFor: Preprocessed Tensor
    
    TruFor->>Model: Forward Pass
    Model->>Model: Extract Features (Encoder)
    Model->>Model: Generate Detection Map (Decoder)
    Model->>Model: Generate Confidence Map
    Model->>Model: Extract Noiseprint Features
    Model-->>TruFor: Raw Outputs (det_map, conf_map, noiseprint)
    
    TruFor->>TruFor: Post-process Results
    TruFor->>TruFor: Calculate Integrity Score
    TruFor->>TruFor: Generate Localization Map
    TruFor->>TruFor: Create Confidence Overlay
    TruFor->>TruFor: Analyze Noiseprint Patterns
    
    TruFor-->>DetectionSvc: Detection Result
    DetectionSvc-->>FastAPI: JSON Response
    FastAPI-->>WebUI: Detection Results
    
    WebUI->>WebUI: Parse Response Data
    WebUI->>WebUI: Update UI Elements
    WebUI->>WebUI: Display Status Badge
    WebUI->>WebUI: Render Visualization Panel
    WebUI->>WebUI: Show Original Image
    WebUI->>WebUI: Display Heatmap Overlay
    WebUI->>WebUI: Enable "Click for details" Button
    
    WebUI-->>User: Show Results
    
    User->>WebUI: Click "Click for details"
    WebUI->>Modal: Show Decision Modal
    Modal->>Modal: Populate Decision Criteria
    Modal->>Modal: Display Thresholds
    Modal->>Modal: Show Analysis Summary
    Modal-->>User: Detailed Analysis View
    
    User->>Modal: Click Close (× or background)
    Modal->>Modal: Hide Modal
    Modal-->>User: Return to Main View
```

### 3. Video Detection Sequence (ResNet Model)

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant DetectionSvc as Detection Service
    participant ResNet as ResNet Adapter
    participant Processor as Media Processor
    participant CV2 as OpenCV

    Note over User,CV2: Video Upload and Frame Analysis

    User->>WebUI: Select Video File
    WebUI->>WebUI: Validate File Type/Size
    WebUI->>FastAPI: POST /detect (video file)
    
    FastAPI->>DetectionSvc: Process Video Upload
    DetectionSvc->>DetectionSvc: Validate MIME Type (video/*)
    DetectionSvc->>DetectionSvc: Validate File Size (<50MB)
    
    DetectionSvc->>ResNet: detect(file_bytes, filename, mime_type)
    
    ResNet->>Processor: Create Temporary File
    Processor->>CV2: Open Video Capture
    CV2->>CV2: Get Video Properties (frame_count, fps)
    CV2->>CV2: Calculate Sample Interval
    
    loop Frame Processing
        CV2->>CV2: Read Next Frame
        alt Sample Frame
            CV2->>Processor: Convert BGR to RGB
            Processor->>Processor: Create PIL Image
            Processor->>ResNet: Preprocess Frame
            ResNet->>ResNet: Apply Transforms
            ResNet->>ResNet: Model Inference
            ResNet->>ResNet: Calculate Probabilities
            ResNet->>ResNet: Store Frame Result
        end
    end
    
    CV2->>Processor: Release Video Capture
    Processor->>Processor: Clean Temporary File
    
    ResNet->>ResNet: Aggregate Frame Results
    ResNet->>ResNet: Calculate Average Probabilities
    ResNet->>ResNet: Determine Overall Prediction
    ResNet->>ResNet: Format Response
    
    ResNet-->>DetectionSvc: Aggregated Result
    DetectionSvc-->>FastAPI: JSON Response
    FastAPI-->>WebUI: Detection Results
    
    WebUI->>WebUI: Display Video Results
    WebUI->>WebUI: Show Frame Analysis Count
    WebUI-->>User: Video Analysis Complete
```

### 4. Error Handling Sequence

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant DetectionSvc as Detection Service
    participant Adapter as Model Adapter

    Note over User,Adapter: Error Scenarios

    User->>WebUI: Upload Invalid File
    WebUI->>FastAPI: POST /detect
    FastAPI->>DetectionSvc: Process Request
    
    alt File Too Large
        DetectionSvc->>DetectionSvc: Check File Size
        DetectionSvc-->>FastAPI: HTTPException(400, "File too large")
        FastAPI-->>WebUI: Error Response
        WebUI-->>User: Show Error Message
    
    else Unsupported Format
        DetectionSvc->>DetectionSvc: Validate MIME Type
        DetectionSvc-->>FastAPI: HTTPException(400, "Unsupported format")
        FastAPI-->>WebUI: Error Response
        WebUI-->>User: Show Error Message
    
    else Model Processing Error
        DetectionSvc->>Adapter: detect()
        Adapter->>Adapter: Process File
        Adapter-->>DetectionSvc: Exception Raised
        DetectionSvc-->>FastAPI: HTTPException(500, "Detection failed")
        FastAPI-->>WebUI: Error Response
        WebUI-->>User: Show Generic Error
    
    else Timeout Error
        DetectionSvc->>Adapter: detect()
        Adapter->>Adapter: Long Processing...
        Adapter-->>DetectionSvc: TimeoutError
        DetectionSvc-->>FastAPI: HTTPException(504, "Timeout")
        FastAPI-->>WebUI: Error Response
        WebUI-->>User: Show Timeout Message
    end
```

### 5. Model Switching Sequence (Runtime)

```mermaid
sequenceDiagram
    participant Admin
    participant Config as Configuration
    participant ModelMgr as Model Manager
    participant OldAdapter as Current Adapter
    participant NewAdapter as New Adapter
    participant FastAPI as FastAPI Server

    Note over Admin,FastAPI: Runtime Model Switching

    Admin->>Config: Update MODEL_TYPE Environment Variable
    Config->>ModelMgr: Trigger Model Reload
    
    ModelMgr->>ModelMgr: Validate New Model Files
    ModelMgr->>NewAdapter: Initialize New Adapter
    NewAdapter->>NewAdapter: Load Model Weights
    NewAdapter->>NewAdapter: Setup Configuration
    NewAdapter-->>ModelMgr: New Adapter Ready
    
    ModelMgr->>FastAPI: Update Detection Adapter
    FastAPI->>OldAdapter: Release Resources
    OldAdapter->>OldAdapter: Cleanup GPU Memory
    OldAdapter->>OldAdapter: Close File Handles
    
    FastAPI->>NewAdapter: Set as Active Adapter
    FastAPI-->>Admin: Model Switch Complete
    
    Note over Admin,FastAPI: New requests now use updated model
```

## Key Sequence Patterns

### 1. **Async Processing**
- All detection operations are asynchronous
- Non-blocking file I/O operations
- Concurrent request handling

### 2. **Error Propagation**
- Structured error handling at each layer
- HTTP status codes for different error types
- User-friendly error messages

### 3. **Resource Management**
- Automatic cleanup of temporary files
- GPU memory management
- Connection pooling for concurrent requests

### 4. **UI Responsiveness**
- Progressive result display
- Modal dialog management
- Real-time status updates

### 5. **Model Abstraction**
- Consistent adapter interface
- Runtime model switching capability
- Fallback mechanisms for model failures

## Performance Considerations

1. **File Size Limits**: Prevent memory exhaustion
2. **Timeout Handling**: Avoid hanging requests
3. **Frame Sampling**: Efficient video processing
4. **Memory Cleanup**: Prevent resource leaks
5. **Caching**: Model weight persistence across requests
