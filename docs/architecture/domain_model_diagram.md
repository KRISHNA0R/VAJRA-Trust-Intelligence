# Deepfake Detection System - Domain Model Diagram

```mermaid
classDiagram
    %% Core Entities
    class DeepfakeDetector {
        +String modelType
        +String device
        +Boolean isOffline
        +detect(MediaFile) DetectionResult
    }
    
    class MediaFile {
        +String filename
        +String mimeType
        +Bytes content
        +Integer size
        +MediaType type
    }
    
    class DetectionResult {
        +String requestId
        +String status
        +Float score
        +String scoreScale
        +List~String~ models
        +List~String~ reasons
        +VendorRawData vendorRaw
    }
    
    class ResNet50Model {
        +String architecture
        +Integer inputSize
        +Integer numClasses
        +String device
        +predict(Tensor) Tensor
        +loadWeights(String) Boolean
    }
    
    class VideoProcessor {
        +Integer sampleInterval
        +Integer maxFrames
        +processVideo(VideoFile) List~Frame~
        +sampleFrames(VideoFile) List~Frame~
    }
    
    class ImageProcessor {
        +Transform transform
        +preprocessImage(Image) Tensor
        +normalizeImage(Image) Tensor
    }
    
    class Frame {
        +Integer frameIndex
        +Image image
        +Float fakeProbability
        +Float authenticProbability
        +Float confidence
    }
    
    class DetectionAdapter {
        <<interface>>
        +detect(MediaFile) DetectionResult
    }
    
    class LocalResNetAdapter {
        +ResNet50Model model
        +ImageProcessor imageProcessor
        +VideoProcessor videoProcessor
        +detect(MediaFile) DetectionResult
        +detectImage(Image) DetectionResult
        +detectVideo(Video) DetectionResult
    }
    
    class APIService {
        +String baseUrl
        +String apiKey
        +uploadFile(MediaFile) String
        +getResult(String) DetectionResult
    }
    
    class WebInterface {
        +String endpoint
        +handleUpload(File) Response
        +displayResult(DetectionResult) Response
    }
    
    class Configuration {
        +String modelPath
        +Boolean useLocalModel
        +String apiKey
        +Integer maxFileSize
        +List~String~ allowedTypes
    }
    
    %% Enums
    class MediaType {
        <<enumeration>>
        IMAGE
        VIDEO
    }
    
    class DetectionStatus {
        <<enumeration>>
        AUTHENTIC
        FAKE
        UNCERTAIN
    }
    
    class FileFormat {
        <<enumeration>>
        JPEG
        PNG
        MP4
        MOV
    }
    
    %% Relationships
    DeepfakeDetector --> MediaFile : processes
    DeepfakeDetector --> DetectionResult : produces
    DeepfakeDetector --> DetectionAdapter : uses
    
    LocalResNetAdapter --|> DetectionAdapter : implements
    LocalResNetAdapter --> ResNet50Model : uses
    LocalResNetAdapter --> ImageProcessor : uses
    LocalResNetAdapter --> VideoProcessor : uses
    
    VideoProcessor --> Frame : creates
    VideoProcessor --> MediaFile : processes
    
    ImageProcessor --> MediaFile : processes
    ImageProcessor --> Frame : processes
    
    ResNet50Model --> Frame : analyzes
    ResNet50Model --> DetectionResult : generates
    
    WebInterface --> DeepfakeDetector : calls
    WebInterface --> MediaFile : receives
    WebInterface --> DetectionResult : returns
    
    Configuration --> DeepfakeDetector : configures
    Configuration --> LocalResNetAdapter : configures
    
    MediaFile --> MediaType : has
    MediaFile --> FileFormat : has
    DetectionResult --> DetectionStatus : has
    
    %% Notes
    note for DeepfakeDetector "Main orchestrator for detection process"
    note for LocalResNetAdapter "Handles offline detection using local ResNet50 model"
    note for ResNet50Model "Core ML model for deepfake classification"
    note for VideoProcessor "Intelligent frame sampling for video analysis"
```

## Key Components Description

### Core Entities
- **DeepfakeDetector**: Main orchestrator that coordinates the detection process
- **MediaFile**: Represents uploaded images or videos with metadata
- **DetectionResult**: Contains the analysis results and confidence scores

### Model Components
- **ResNet50Model**: The core machine learning model for classification
- **LocalResNetAdapter**: Adapter that implements offline detection using ResNet50
- **ImageProcessor**: Handles image preprocessing and normalization
- **VideoProcessor**: Manages video frame sampling and processing

### Processing Flow
1. **MediaFile** is uploaded through **WebInterface**
2. **DeepfakeDetector** receives the file and delegates to appropriate adapter
3. **LocalResNetAdapter** processes the file using **ResNet50Model**
4. For videos, **VideoProcessor** samples frames and processes each frame
5. **ImageProcessor** preprocesses each frame/image
6. **ResNet50Model** analyzes the processed data
7. Results are aggregated and returned as **DetectionResult**

### Security Features
- Complete offline operation (no external API calls)
- Local data processing only
- Configurable model paths and settings
- Support for multiple media formats
