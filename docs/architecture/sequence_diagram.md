# Deepfake Detection System - Sequence Diagram

## Main Detection Flow

```mermaid
sequenceDiagram
    participant User as User
    participant WebUI as Web Interface
    participant API as FastAPI Server
    participant Adapter as LocalResNetAdapter
    participant Model as ResNet50Model
    participant Processor as ImageProcessor
    participant VideoProc as VideoProcessor
    participant Frame as Video Frame

    User->>WebUI: Upload media file
    WebUI->>API: POST /detect (file)
    
    API->>API: Validate file type & size
    API->>Adapter: detect(file_bytes, filename, mime_type)
    
    alt Image Detection
        Adapter->>Processor: preprocessImage(image)
        Processor->>Processor: resize(224x224)
        Processor->>Processor: normalize()
        Processor-->>Adapter: preprocessed_tensor
        
        Adapter->>Model: predict(tensor)
        Model->>Model: forward_pass()
        Model-->>Adapter: probabilities
        
        Adapter->>Adapter: calculate_confidence()
        Adapter-->>API: DetectionResult
        
    else Video Detection
        Adapter->>VideoProc: processVideo(video_bytes)
        VideoProc->>VideoProc: extract_frames()
        VideoProc->>VideoProc: sample_frames(interval)
        
        loop For each sampled frame
            VideoProc->>Frame: create_frame()
            VideoProc->>Processor: preprocessImage(frame)
            Processor->>Processor: resize(224x224)
            Processor->>Processor: normalize()
            Processor-->>VideoProc: preprocessed_tensor
            
            VideoProc->>Model: predict(tensor)
            Model->>Model: forward_pass()
            Model-->>VideoProc: probabilities
            
            VideoProc->>VideoProc: store_frame_result()
        end
        
        VideoProc->>VideoProc: aggregate_results()
        VideoProc-->>Adapter: aggregated_result
        Adapter-->>API: DetectionResult
    end
    
    API->>API: format_response()
    API-->>WebUI: JSON response
    WebUI-->>User: Display results
```

## Model Loading Sequence

```mermaid
sequenceDiagram
    participant Server as FastAPI Server
    participant Adapter as LocalResNetAdapter
    participant Model as ResNet50Model
    participant FileSystem as File System

    Server->>Server: Application startup
    Server->>Adapter: LocalResNetAdapter(model_path)
    
    Adapter->>FileSystem: check_file_exists(model_path)
    FileSystem-->>Adapter: file_exists: true
    
    Adapter->>Model: ResNet50(pretrained=False)
    Model-->>Adapter: model_instance
    
    Adapter->>Model: modify_fc_layer(num_classes=2)
    Model-->>Adapter: modified_model
    
    Adapter->>FileSystem: load_checkpoint(model_path)
    FileSystem-->>Adapter: checkpoint_data
    
    Adapter->>Model: load_state_dict(checkpoint)
    Model-->>Adapter: weights_loaded
    
    Adapter->>Model: to(device)
    Model-->>Adapter: model_on_device
    
    Adapter->>Model: eval()
    Model-->>Adapter: model_ready
    
    Adapter-->>Server: initialization_complete
    Server-->>Server: ready_to_serve
```

## Error Handling Sequence

```mermaid
sequenceDiagram
    participant User as User
    participant WebUI as Web Interface
    participant API as FastAPI Server
    participant Adapter as LocalResNetAdapter
    participant Model as ResNet50Model

    User->>WebUI: Upload invalid file
    WebUI->>API: POST /detect (invalid_file)
    
    API->>API: Validate file type & size
    
    alt Invalid File Type
        API-->>WebUI: HTTP 400 (Unsupported file type)
        WebUI-->>User: Error message
    else File Too Large
        API-->>WebUI: HTTP 400 (File too large)
        WebUI-->>User: Error message
    else Valid File
        API->>Adapter: detect(file_bytes, filename, mime_type)
        
        alt Model Loading Error
            Adapter-->>API: ModelLoadError
            API-->>WebUI: HTTP 500 (Model loading failed)
            WebUI-->>User: Error message
        else Detection Error
            Adapter->>Model: predict(tensor)
            Model-->>Adapter: DetectionError
            Adapter-->>API: DetectionError
            API-->>WebUI: HTTP 500 (Detection failed)
            WebUI-->>User: Error message
        else Success
            Adapter-->>API: DetectionResult
            API-->>WebUI: Success response
            WebUI-->>User: Display results
        end
    end
```

## Video Processing Detail

```mermaid
sequenceDiagram
    participant Adapter as LocalResNetAdapter
    participant VideoProc as VideoProcessor
    participant OpenCV as OpenCV
    participant Frame as Frame
    participant Model as ResNet50Model
    participant Processor as ImageProcessor

    Adapter->>VideoProc: detect_video(video_bytes)
    VideoProc->>OpenCV: VideoCapture(video_path)
    OpenCV-->>VideoProc: video_handle
    
    VideoProc->>OpenCV: get_frame_count()
    OpenCV-->>VideoProc: total_frames
    
    VideoProc->>VideoProc: calculate_sample_interval()
    VideoProc->>VideoProc: initialize_frame_arrays()
    
    loop Process each frame
        VideoProc->>OpenCV: read_frame()
        OpenCV-->>VideoProc: frame_data
        
        alt Frame should be sampled
            VideoProc->>Frame: create_frame(frame_data, frame_idx)
            VideoProc->>Processor: preprocessImage(frame)
            Processor->>Processor: convert_BGR_to_RGB()
            Processor->>Processor: resize(224x224)
            Processor->>Processor: normalize()
            Processor-->>VideoProc: preprocessed_tensor
            
            VideoProc->>Model: predict(tensor)
            Model->>Model: forward_pass()
            Model-->>VideoProc: probabilities
            
            VideoProc->>VideoProc: store_frame_result()
        end
    end
    
    VideoProc->>VideoProc: aggregate_frame_predictions()
    VideoProc->>VideoProc: calculate_average_confidence()
    VideoProc-->>Adapter: video_detection_result
    
    VideoProc->>OpenCV: release()
    OpenCV-->>VideoProc: video_closed
```

## Key Components Description

### Main Detection Flow
- Shows the complete process from user upload to result display
- Handles both image and video detection paths
- Demonstrates the decision flow for different media types

### Model Loading Sequence
- Details the initialization process of the ResNet50 model
- Shows file validation, model creation, and weight loading
- Illustrates the device configuration and model preparation

### Error Handling Sequence
- Covers various error scenarios and their handling
- Shows proper HTTP status codes and error messages
- Demonstrates graceful error recovery

### Video Processing Detail
- Deep dive into video frame processing
- Shows OpenCV integration and frame sampling
- Illustrates the aggregation of multiple frame results

## Processing Characteristics

- **Offline Operation**: All processing happens locally
- **Intelligent Sampling**: Videos are processed using smart frame sampling
- **Error Resilience**: Comprehensive error handling at each step
- **Resource Management**: Proper cleanup of temporary files and resources
- **Scalable Architecture**: Easy to extend for different model types
