# Deepfake Detection System V2 - Domain Model Diagram

## System Overview
Version 2 introduces advanced TruFor model integration with pixel-level detection capabilities, enhanced UI with modal dialogs, and improved configuration management.

## Domain Model Diagram

```mermaid
classDiagram
    class FastAPIApplication {
        +title: str
        +version: str
        +description: str
        +startup()
        +shutdown()
        +mount_static_files()
        +configure_cors()
    }

    class DetectionService {
        +detection_adapter: BaseAdapter
        +max_image_size: int
        +max_video_size: int
        +detect_deepfake(): JSONResponse
        +validate_file(): bool
        +health_check(): dict
    }

    class BaseAdapter {
        <<interface>>
        +detect(): Dict
    }

    class TruForAdapter {
        +model_path: str
        +device: str
        +model: EncoderDecoder
        +config: Config
        +_setup_device()
        +_load_model()
        +_preprocess_image()
        +_postprocess_results()
        +_calculate_integrity_score()
        +_generate_localization_map()
        +_create_confidence_map()
        +detect()
    }

    class LocalResNetAdapter {
        +model_path: str
        +device: str
        +model: ResNet50
        +transform: Compose
        +_load_model()
        +_setup_transforms()
        +_detect_image()
        +_detect_video()
        +_format_response()
        +detect()
    }

    class TruForModel {
        +encoder: DualSegformer
        +decoder: MLPDecoder
        +noiseprint_extractor: NoiseNet
        +forward()
        +extract_features()
        +generate_detection_map()
        +generate_confidence_map()
    }

    class NoiseNet {
        +layers: Sequential
        +extract_noiseprint()
        +preprocess_image()
    }

    class ConfigManager {
        +model_type: str
        +model_path: str
        +server_config: dict
        +ui_config: dict
        +logging_config: dict
        +load_config()
        +validate_config()
    }

    class MediaProcessor {
        +supported_formats: Set
        +max_sizes: dict
        +validate_mime_type()
        +validate_file_size()
        +extract_video_frames()
        +preprocess_image()
    }

    class DetectionResult {
        +request_id: str
        +media_type: str
        +status: str
        +score: float
        +score_scale: str
        +models: List
        +reasons: List
        +vendor_raw: dict
        +integrity: float
        +localization_map: List
        +confidence_map: List
        +noiseprint_analysis: dict
    }

    class VisualizationData {
        +original_image: str
        +detection_heatmap: str
        +confidence_overlay: str
        +noiseprint_visualization: str
        +localization_regions: List
        +generate_heatmap()
        +create_overlay()
    }

    class WebInterface {
        +upload_component: FileUploader
        +result_display: ResultViewer
        +modal_dialog: DecisionModal
        +visualization_panel: VisualizationPanel
        +handle_file_upload()
        +display_results()
        +show_decision_details()
    }

    class DecisionModal {
        +modal_element: HTMLElement
        +decision_details: HTMLElement
        +show()
        +hide()
        +populate_content()
        +handle_close_events()
    }

    class VisualizationPanel {
        +canvas_container: HTMLElement
        +original_display: HTMLElement
        +heatmap_display: HTMLElement
        +confidence_display: HTMLElement
        +render_original()
        +render_heatmap()
        +render_confidence_map()
        +create_interactive_overlay()
    }

    class ModelManager {
        +available_models: dict
        +active_model: str
        +model_cache: dict
        +load_model()
        +switch_model()
        +validate_model_files()
        +download_models()
    }

    FastAPIApplication --> DetectionService
    DetectionService --> BaseAdapter
    BaseAdapter <|-- TruForAdapter
    BaseAdapter <|-- LocalResNetAdapter
    
    TruForAdapter --> TruForModel
    TruForAdapter --> ConfigManager
    TruForAdapter --> MediaProcessor
    
    TruForModel --> NoiseNet
    
    DetectionService --> DetectionResult
    DetectionResult --> VisualizationData
    
    WebInterface --> DecisionModal
    WebInterface --> VisualizationPanel
    
    FastAPIApplication --> ModelManager
    ModelManager --> BaseAdapter
```

## Key Domain Concepts

### 1. **Multi-Model Architecture**
- **TruForAdapter**: Advanced forensic model with pixel-level detection
- **LocalResNetAdapter**: Fast binary classification model
- **BaseAdapter**: Common interface ensuring consistency

### 2. **Enhanced Detection Results**
- **Integrity Score**: Overall authenticity assessment
- **Localization Maps**: Pixel-level manipulation detection
- **Confidence Maps**: Reliability assessment for each region
- **Noiseprint Analysis**: Digital fingerprint analysis

### 3. **Improved User Interface**
- **Decision Modal**: Centered modal with detailed analysis
- **Visualization Panel**: Multi-layer result display
- **Interactive Elements**: Hover effects and detailed breakdowns

### 4. **Configuration Management**
- **Model Selection**: Runtime model switching capability
- **Environment Configuration**: Flexible deployment options
- **Resource Management**: Memory and GPU optimization

### 5. **Media Processing Pipeline**
- **Format Validation**: Support for images and videos
- **Size Constraints**: Configurable file size limits
- **Preprocessing**: Standardized input preparation

## Version 2 Enhancements

1. **TruFor Integration**: State-of-the-art forensic analysis
2. **Pixel-Level Detection**: Precise manipulation localization
3. **Enhanced Visualization**: Multi-layer result presentation
4. **Improved UI**: Better modal positioning and user experience
5. **Configuration System**: Centralized settings management
6. **Model Management**: Dynamic model loading and switching
7. **Error Handling**: Comprehensive error recovery
8. **Internationalization**: English translation of all components
