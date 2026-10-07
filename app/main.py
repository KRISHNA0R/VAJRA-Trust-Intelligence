import logging
import os
import json
import time
import hashlib
import asyncio
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

try:
    # Try relative imports first (when run from app directory)
    from adapters.trufor_adapter import TruForAdapter
    from adapters.deepfakebench_adapter import DeepfakeBenchAdapter
    from adapters.audio_adapter import AudioSpoofAdapter
    from auth.user_manager import user_manager
    from auth.decorators import get_current_user, get_current_admin, get_optional_user
    from history.history_manager import history_manager
    from reports.pdf_generator import generate_pdf_report
    from reports.zip_generator import generate_zip_report
    from utils.risk import attach as attach_risk
except ImportError:
    # Fallback to absolute imports (when run from project root)
    from app.adapters.trufor_adapter import TruForAdapter
    from app.adapters.deepfakebench_adapter import DeepfakeBenchAdapter
    from app.adapters.audio_adapter import AudioSpoofAdapter
    from app.auth.user_manager import user_manager
    from app.auth.decorators import get_current_user, get_current_admin, get_optional_user
    from app.history.history_manager import history_manager
    from app.reports.pdf_generator import generate_pdf_report
    from app.reports.zip_generator import generate_zip_report
    from app.utils.risk import attach as attach_risk

import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize adapter as global variable
detection_adapter = None
audio_adapter = None

# Thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=2)

# Job storage
jobs = {}

# Constants for video analysis
DATA_DIR = Path("data/jobs")
DATA_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup"""
    global detection_adapter
    try:
        # Initialize TruFor model
        model_path = os.getenv("MODEL_PATH", "models/trufor.pth.tar")
        if os.path.exists(model_path):
            detection_adapter = TruForAdapter(model_path=model_path)
            logger.info("TruFor adapter initialized successfully")
        else:
            logger.warning(f"TruFor model not found at {model_path}, adapter not initialized")
            detection_adapter = None
            
    except Exception as e:
        logger.error(f"Failed to initialize detection adapter: {e}")
        logger.warning("Server will start without TruFor model loaded")
        detection_adapter = None
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="VAJRA Trust Intelligence API",
    version="1.0.0",
    description="Verification & AI-based Judgement for Risk Assessment - deepfake detection service supporting TruFor and DeepfakeBench models",
    lifespan=lifespan
)

# Mount static files
app.mount("/web", StaticFiles(directory="app/web"), name="web")
app.mount("/static", StaticFiles(directory=".", html=True), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Constants
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",  # AVI
    "video/mpeg",
    "video/webm",
    "video/x-matroska",  # MKV
    "application/octet-stream"  # Generic binary, for some MP4 files
}
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_AUDIO_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/ogg",
    "audio/flac",
    "audio/x-flac",
    "audio/mp4",
    "audio/x-m4a",
    "audio/aac",
    "audio/webm",
    "application/octet-stream",  # Generic binary, for odd client MIME types
}


# =============================================================================
# Pydantic Models for Request/Response
# =============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "investigator"
    email: str = ""


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# =============================================================================
# Authentication API Endpoints
# =============================================================================

@app.post("/api/auth/register")
async def register_user(request: RegisterRequest):
    """Register a new user"""
    
    allowed_roles = {"analyst", "investigator"}
    if request.role not in allowed_roles:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid role. Must be one of: {', '.join(allowed_roles)}"
        )
    try:    
        user = user_manager.create_user(
            username=request.username,
            password=request.password,
            role=request.role,
            email=request.email
        )
        
        user_data = {
            "username": user.get("username"),
            "role": user.get("role"),
            "email": user.get("email")
        }
        return JSONResponse(content={"success": True, "user": user_data})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    user = user_manager.authenticate_user(request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    # Update last login
    user_manager.update_last_login(request.username)

    # Create token
    token = user_manager.create_access_token(user["username"], user["role"])

    return JSONResponse(content={
        "access_token": token,
        "token_type": "bearer",
        "user": user
    })


# Compatibility aliases for testing and OAuth2 standard
@app.post("/register")
async def register_user_alias(request: RegisterRequest):
    """Alias for /api/auth/register (for compatibility)"""
    return await register_user(request)


@app.post("/token")
async def token_alias(username: str = Form(...), password: str = Form(...)):
    """OAuth2 compatible token endpoint (for compatibility)"""
    request = LoginRequest(username=username, password=password)
    return await login(request)


@app.post("/api/auth/logout")
async def logout(
    user: dict = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """Logout user (revoke token)"""
    if authorization:
        try:
            _, token = authorization.split()
            user_manager.revoke_token(token)
        except ValueError:
            pass

    return JSONResponse(content={"success": True, "message": "Logged out successfully"})


@app.get("/api/auth/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current user information"""
    user_data = user_manager.get_user(user["username"])
    if user_data:
        return JSONResponse(content={k: v for k, v in user_data.items() if k != "password_hash"})

    raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/auth/users")
async def list_users(admin: dict = Depends(get_current_admin)):
    """List all users (admin only)"""
    users = user_manager.list_users()
    return JSONResponse(content={"users": users})


@app.patch("/api/auth/users/{username}")
async def update_user(
    username: str,
    request: UpdateUserRequest,
    admin: dict = Depends(get_current_admin)
):
    """Update user information (admin only)"""
    try:
        updated_user = user_manager.update_user(
            username,
            **{k: v for k, v in request.dict().items() if v is not None}
        )
        return JSONResponse(content={"success": True, "user": updated_user})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/auth/users/{username}")
async def delete_user(username: str, admin: dict = Depends(get_current_admin)):
    """Delete user (admin only)"""
    try:
        user_manager.delete_user(username)
        return JSONResponse(content={"success": True, "message": f"User {username} deleted"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/change-password")
async def change_password(
    request: ChangePasswordRequest,
    user: dict = Depends(get_current_user)
):
    """Change user password"""
    try:
        user_manager.change_password(
            user["username"],
            request.old_password,
            request.new_password
        )
        return JSONResponse(content={"success": True, "message": "Password changed successfully"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# History API Endpoints
# =============================================================================

@app.get("/api/history")
async def get_history(
    user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
):
    """Get detection history for current user"""
    history = history_manager.get_user_history(
        username=user["username"],
        role=user["role"],
        limit=limit,
        offset=offset,
        status=status
    )
    return JSONResponse(content=history)


@app.get("/api/history/stats")
async def get_history_stats(user: dict = Depends(get_current_user)):
    """Get detection statistics for current user"""
    stats = history_manager.get_statistics(
        username=user["username"],
        role=user["role"]
    )
    return JSONResponse(content=stats)


@app.get("/api/history/{job_id}")
async def get_job_details(job_id: str, user: dict = Depends(get_current_user)):
    """Get detailed information about a specific job"""
    details = history_manager.get_job_details(
        job_id=job_id,
        username=user["username"],
        role=user["role"]
    )

    if not details:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    return JSONResponse(content=details)


@app.delete("/api/history/{job_id}")
async def delete_job(job_id: str, user: dict = Depends(get_current_user)):
    """Delete a detection job"""
    try:
        success = history_manager.delete_job(
            job_id=job_id,
            username=user["username"],
            role=user["role"]
        )

        if success:
            # Also remove from in-memory jobs dict
            if job_id in jobs:
                del jobs[job_id]

            return JSONResponse(content={"success": True, "message": "Job deleted"})
        else:
            raise HTTPException(status_code=404, detail="Job not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# =============================================================================
# Report Generation API Endpoints
# =============================================================================

@app.get("/api/reports/{job_id}/pdf")
async def download_pdf_report(job_id: str, user: dict = Depends(get_current_user)):
    """Download PDF report for a job"""
    # Check access permission
    details = history_manager.get_job_details(
        job_id=job_id,
        username=user["username"],
        role=user["role"]
    )

    if not details:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    job_dir = DATA_DIR / job_id
    pdf_path = job_dir / "report.pdf"

    # Generate PDF if it doesn't exist
    if not pdf_path.exists():
        try:
            generate_pdf_report(job_id, str(job_dir), details)
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate PDF report")

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF report not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{job_id}_report.pdf"
    )


@app.get("/api/reports/{job_id}/zip")
async def download_zip_report(
    job_id: str,
    user: dict = Depends(get_current_user),
    include_video: bool = True
):
    """Download ZIP archive containing all job artifacts"""
    # Check access permission
    details = history_manager.get_job_details(
        job_id=job_id,
        username=user["username"],
        role=user["role"]
    )

    if not details:
        raise HTTPException(status_code=404, detail="Job not found or access denied")

    job_dir = DATA_DIR / job_id
    zip_path = job_dir / "report.zip"

    # Generate ZIP if it doesn't exist or needs update
    try:
        generate_zip_report(str(job_dir), include_video=include_video)
    except Exception as e:
        logger.error(f"Failed to generate ZIP report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate ZIP report")

    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP report not found")

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{job_id}_report.zip"
    )


# =============================================================================
# Health & Root Endpoints
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vajra-trust-intelligence", "timestamp": datetime.now().isoformat()}


@app.get("/api/models/status")
async def get_models_status(user: dict = Depends(get_current_user)):
    """Get status of all detection models (requires authentication)"""
    from pathlib import Path
    from tools.weight_registry import WEIGHT_REGISTRY
    
    # Check TruFor model
    trufor_path = Path("models/trufor.pth.tar")
    trufor_available = trufor_path.exists()
    
    # Check DeepfakeBench models
    weights_dir = Path("models/vendors/DeepfakeBench/training/weights")
    available_models = []
    
    if weights_dir.exists():
        for weight_file, config in WEIGHT_REGISTRY.items():
            weight_path = weights_dir / weight_file
            if weight_path.exists():
                available_models.append(config["model_key"])
    
    return {
        "trufor": {
            "available": trufor_path.exists(),
            "path": str(trufor_path) if trufor_path.exists() else None
        },
        "deepfakebench": {
            "available_models": available_models,
            "total_models": len(WEIGHT_REGISTRY)
        },
        "audio": {
            "available": Path("models/audio_dhwani/best_model.onnx").exists(),
            "model": "dhwani-spoof"
        }
    }


@app.post("/detect")
async def detect_deepfake(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Detect deepfakes in uploaded media files (requires authentication)

    Accepts:
    - Images: JPEG, PNG (max 10MB)
    - Videos: MP4, MOV (max 50MB)

    Returns detection results including confidence score and verdict
    """
    # Validate MIME type
    mime_type = file.content_type
    if mime_type not in (ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {mime_type}. Allowed: JPEG, PNG, MP4, MOV"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    is_video = mime_type in ALLOWED_VIDEO_TYPES
    max_size = MAX_VIDEO_SIZE if is_video else MAX_IMAGE_SIZE
    if len(content) > max_size:
        size_limit_mb = max_size // (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {size_limit_mb}MB"
        )

    # Log request (without content)
    media_type = "video" if is_video else "image"
    logger.info(f"User {user['username']} processing {media_type}: {file.filename} ({len(content)} bytes)")

    # Generate job ID for tracking
    timestamp = int(time.time())
    file_hash = hashlib.sha256(content).hexdigest()[:12]
    job_id = f"trufor_{file_hash}_{timestamp}"

    try:
        # Call detection adapter
        result = await detection_adapter.detect(
            file_bytes=content,
            filename=file.filename,
            mime_type=mime_type
        )

        # Generate and save heatmap visualizations for TruFor results
        if result.get("status") == "success" and mime_type.startswith('image/'):
            try:
                import matplotlib
                matplotlib.use('Agg')  # Non-interactive backend
                import matplotlib.pyplot as plt
                import numpy as np

                # Create job directory for storing visualizations
                job_dir = DATA_DIR / job_id
                job_dir.mkdir(parents=True, exist_ok=True)

                # Generate anomaly heatmap (prediction_map or weighted_prediction_map)
                if "weighted_prediction_map" in result and result["weighted_prediction_map"]:
                    weighted_map = np.array(result["weighted_prediction_map"])
                    fig, ax = plt.subplots(figsize=(10, 10))
                    im = ax.imshow(weighted_map, cmap='jet', vmin=0, vmax=1)
                    ax.set_title("Anomaly Detection Heatmap (Confidence-Weighted)", fontsize=14, fontweight='bold')
                    ax.axis('off')
                    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                    cbar.set_label('Anomaly Score', rotation=270, labelpad=20)
                    heatmap_path = job_dir / f"{job_id}_heatmap.png"
                    plt.savefig(heatmap_path, dpi=150, bbox_inches='tight')
                    plt.close()
                    logger.info(f"Saved anomaly heatmap to {heatmap_path}")
                elif "prediction_map" in result and result["prediction_map"]:
                    pred_map = np.array(result["prediction_map"])
                    fig, ax = plt.subplots(figsize=(10, 10))
                    im = ax.imshow(pred_map, cmap='jet', vmin=0, vmax=1)
                    ax.set_title("Anomaly Detection Heatmap", fontsize=14, fontweight='bold')
                    ax.axis('off')
                    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                    cbar.set_label('Anomaly Score', rotation=270, labelpad=20)
                    heatmap_path = job_dir / f"{job_id}_heatmap.png"
                    plt.savefig(heatmap_path, dpi=150, bbox_inches='tight')
                    plt.close()
                    logger.info(f"Saved anomaly heatmap to {heatmap_path}")

                # Generate confidence map
                if "confidence_map" in result and result["confidence_map"]:
                    conf_map = np.array(result["confidence_map"])
                    fig, ax = plt.subplots(figsize=(10, 10))
                    im = ax.imshow(conf_map, cmap='viridis', vmin=0, vmax=1)
                    ax.set_title("Model Confidence Map", fontsize=14, fontweight='bold')
                    ax.axis('off')
                    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                    cbar.set_label('Confidence', rotation=270, labelpad=20)
                    conf_path = job_dir / f"{job_id}_conf.png"
                    plt.savefig(conf_path, dpi=150, bbox_inches='tight')
                    plt.close()
                    logger.info(f"Saved confidence map to {conf_path}")

                # Generate noiseprint++ map if available
                if result.get("has_noiseprint") and "noiseprint_map" in result and result["noiseprint_map"]:
                    npp_map = np.array(result["noiseprint_map"])
                    fig, ax = plt.subplots(figsize=(10, 10))
                    im = ax.imshow(npp_map, cmap='gray', vmin=0, vmax=1)
                    ax.set_title("Noiseprint++ Forensic Analysis", fontsize=14, fontweight='bold')
                    ax.axis('off')
                    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                    cbar.set_label('Noise Pattern', rotation=270, labelpad=20)
                    npp_path = job_dir / f"{job_id}_noiseprint.png"
                    plt.savefig(npp_path, dpi=150, bbox_inches='tight')
                    plt.close()
                    logger.info(f"Saved noiseprint map to {npp_path}")

            except Exception as e:
                logger.warning(f"Failed to generate heatmap visualizations for job {job_id}: {e}")
                import traceback
                traceback.print_exc()

        # Financial risk assessment (shared playbook)
        attach_risk(result)  # adds risk_level + recommended_actions in place
        risk_level = result["risk_level"]
        risk_actions = result["recommended_actions"]

        # Create metadata for history
        history_manager.create_job_metadata(
            job_id=job_id,
            username=user["username"],
            filename=file.filename,
            detection_type="trufor",
            model="trufor"
        )

        # Update job status with result
        history_manager.update_job_status(
            job_id=job_id,
            status="completed",
            result={
                # Core verdict and scores
                "verdict": result.get("decision", "unknown"), # Use 'decision' field
                "confidence": result.get("confidence", 0),   # Prediction strength (0-1)
                "score": result.get("score", 0),             # Authenticity score (0-1, 1=real)
                "integrity": result.get("integrity", 0),     # Integrity score (TruFor specific)
                "fake_prob": result.get("fake_prob", 0),     # Raw fake probability
                "risk_level": risk_level,
                "recommended_actions": risk_actions,

                # Metadata about the analysis
                "image_size": result.get("image_size", None), # Original (H, W)
                "has_confidence_map": result.get("has_confidence_map", False),
                "has_noiseprint": result.get("has_noiseprint", False),
                "portrait_note": result.get("portrait_note", "") # Portrait mode hint
            }
        )

        logger.info(f"Detection complete for {file.filename}: {result['status']}")
        
        # BUGFIX-007: Downsample huge heatmap arrays before sending to frontend
        # This prevents browser crashes when processing large images
        def downsample_array(data, max_size=300):
            """Downsample 2D array to max_size x max_size while preserving aspect ratio"""
            if not data or not isinstance(data, list):
                return data
            
            import numpy as np
            arr = np.array(data)
            if arr.size == 0:
                return data
            
            height, width = arr.shape
            if height <= max_size and width <= max_size:
                return data  # No downsampling needed
            
            # Calculate new dimensions preserving aspect ratio
            if width > height:
                new_width = max_size
                new_height = max(1, int(max_size * height / width))
            else:
                new_height = max_size
                new_width = max(1, int(max_size * width / height))
            
            # Downsample using simple averaging
            from scipy import ndimage
            zoom_factors = (new_height / height, new_width / width)
            downsampled = ndimage.zoom(arr, zoom_factors, order=1)  # Bilinear interpolation
            
            return downsampled.tolist()
        
        # Downsample large arrays and update image_size accordingly
        downsampled = False
        for key in ['prediction_map', 'confidence_map', 'weighted_prediction_map', 'noiseprint_map']:
            if key in result and result[key]:
                original_data = result[key]
                result[key] = downsample_array(original_data, max_size=300)
                
                # Update image_size to match downsampled data
                if not downsampled and result[key] != original_data:
                    import numpy as np
                    arr = np.array(result[key])
                    result["image_size"] = arr.shape  # Update to downsampled size
                    downsampled = True
        
        result["job_id"] = job_id  # Add job_id to response
        
        return JSONResponse(content=result)

    except TimeoutError:
        logger.error(f"Timeout processing {file.filename}")
        raise HTTPException(
            status_code=504,
            detail="Detection timeout - file may be too complex"
        )
    except Exception as e:
        logger.error(f"Detection failed for {file.filename}: {e}")
        # Check if it's a vendor service issue
        if "reality defender" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="Detection service temporarily unavailable"
            )
        raise HTTPException(
            status_code=500,
            detail="Detection failed - please try again"
        )


@app.get("/", response_class=FileResponse)
async def root():
    """Serve the main HTML page"""
    return FileResponse('app/web/index.html')


@app.post("/video/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze video for deepfake detection and generate timeline
    Returns job_id for tracking progress
    """
    logger.info(f"Received video upload: filename={file.filename}, content_type={file.content_type}")
    
    # Validate file type
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        logger.error(f"Unsupported file type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: MP4, MOV, AVI, MPEG, WebM, MKV"
        )
    
    # Read file content
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    logger.info(f"File size: {file_size_mb:.2f}MB")
    
    # Validate size
    if len(content) > MAX_VIDEO_SIZE:
        logger.error(f"File too large: {file_size_mb:.2f}MB > {MAX_VIDEO_SIZE/(1024*1024)}MB")
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size_mb:.1f}MB. Maximum size: 500MB"
        )
    
    # Generate job ID
    timestamp = int(time.time())
    file_hash = hashlib.sha256(content).hexdigest()[:12]
    job_id = f"job_{file_hash}_{timestamp}"
    
    # Create job directory
    job_dir = DATA_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # Save input video
    input_path = job_dir / "input.mp4"
    with open(input_path, "wb") as f:
        f.write(content)
    
    logger.info(f"Created job {job_id} for video {file.filename} ({len(content)} bytes)")
    
    # Initialize job status
    jobs[job_id] = {
        "status": "processing",
        "job_id": job_id,
        "filename": file.filename,
        "created_at": timestamp,
        "progress": 0,
        "message": "Starting analysis..."
    }
    
    # Start analysis in background
    asyncio.create_task(run_video_analysis(job_id, str(input_path), str(job_dir)))
    
    return JSONResponse(content={"job_id": job_id})


async def run_video_analysis(job_id: str, input_path: str, output_dir: str):
    """Run video analysis in background"""
    try:
        logger.info(f"Starting OFFICIAL DeepfakeBench video analysis for job {job_id}")
        
        # Path to inference script
        inference_script = "models/vendors/DeepfakeBench/tools/video_inference.py"
        weights_path = "models/vendors/DeepfakeBench/training/weights/videomae_pretrained.pth"
        
        # Check if weights exist
        if not os.path.exists(weights_path):
            logger.warning(f"VideoMAE weights not found at {weights_path}")
            logger.warning("Please download official weights from: https://github.com/SCLBD/DeepfakeBench/releases")
        
        # Build command
        cmd = [
            "python",
            inference_script,
            "--input", input_path,
            "--out", output_dir,
            "--weights", weights_path,
            "--threshold-percentile", "85"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Run subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for completion
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Load timeline results
            timeline_path = Path(output_dir) / "timeline.json"
            if timeline_path.exists():
                with open(timeline_path, 'r') as f:
                    timeline = json.load(f)
                
                jobs[job_id].update({
                    "status": "completed",
                    "progress": 100,
                    "message": "Analysis complete",
                    "result": timeline
                })
                logger.info(f"Job {job_id} completed successfully using OFFICIAL pipeline")
            else:
                jobs[job_id].update({
                    "status": "error",
                    "message": "Timeline file not found"
                })
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error(f"Job {job_id} failed: {error_msg}")
            jobs[job_id].update({
                "status": "error",
                "message": f"Analysis failed: {error_msg[:200]}"
            })
            
    except Exception as e:
        logger.error(f"Job {job_id} error: {e}")
        jobs[job_id].update({
            "status": "error",
            "message": str(e)
        })


@app.get("/video/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Get job status and progress"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # Check for progress updates from inference script
    job_dir = DATA_DIR / job_id
    progress_file = job_dir / "progress.json"
    
    if progress_file.exists():
        try:
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
                job.update({
                    "progress": progress_data.get("progress", job.get("progress", 0)),
                    "message": progress_data.get("message", job.get("message", "")),
                    "stage": progress_data.get("stage", "processing")
                })
        except Exception as e:
            logger.warning(f"Failed to read progress file: {e}")
    
    return JSONResponse(content=job)


@app.get("/video/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    """Get complete analysis results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Current status: {job['status']}"
        )
    
    return JSONResponse(content=job.get("result", {}))


@app.get("/video/jobs/{job_id}/keyframes/{filename}")
async def get_keyframe(job_id: str, filename: str):
    """Serve keyframe images"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    keyframe_path = DATA_DIR / job_id / "keyframes" / filename
    
    if not keyframe_path.exists():
        raise HTTPException(status_code=404, detail="Keyframe not found")
    
    return FileResponse(keyframe_path)


# =============================================================================
# DeepfakeBench API Endpoints
# =============================================================================

@app.get("/api/deepfakebench/models")
async def get_deepfakebench_models():
    """Get list of available DeepfakeBench models"""
    try:
        models = DeepfakeBenchAdapter.get_available_models()
        return JSONResponse(content={"models": models})
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deepfakebench/analyze")
async def analyze_with_deepfakebench(
    file: UploadFile = File(...),
    model: str = Form("xception"),
    fps: float = Form(3.0),
    threshold: float = Form(0.5),
    user: dict = Depends(get_current_user)
):
    """
    Analyze video using DeepfakeBench models (requires authentication)

    Parameters:
    - file: Video file
    - model: Model key (e.g., 'xception', 'meso4', 'f3net')
    - fps: Frame sampling rate (default: 3.0)
    - threshold: Detection threshold (default: 0.5)
    """
    # Validate file type
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )

    # Read file content
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    logger.info(f"User {user['username']} - DeepfakeBench analysis request - File: {file.filename}, Size: {file_size_mb:.2f}MB, Model: {model}")

    # Validate size
    if len(content) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size_mb:.1f}MB. Maximum size: 500MB"
        )

    # Generate job ID
    timestamp = int(time.time())
    file_hash = hashlib.sha256(content).hexdigest()[:12]
    job_id = f"dfb_{file_hash}_{timestamp}"

    logger.info(f"Created DeepfakeBench job {job_id} for user {user['username']}, video {file.filename}")

    # Initialize job status FIRST (before saving file)
    jobs[job_id] = {
        "status": "processing",
        "job_id": job_id,
        "filename": file.filename,
        "model": model,
        "created_at": timestamp,
        "progress": 0,
        "stage": "Uploading...",
        "message": f"Preparing to analyze with {model}"
    }

    # Create metadata for history
    history_manager.create_job_metadata(
        job_id=job_id,
        username=user["username"],
        filename=file.filename,
        detection_type="deepfakebench",
        model=model
    )

    # Start analysis in background thread (to avoid blocking event loop)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        executor,
        run_deepfakebench_analysis_sync,
        job_id, content, model, fps, threshold
    )

    # Return job_id IMMEDIATELY (before file is saved)
    return JSONResponse(content={"job_id": job_id, "model": model})


def run_deepfakebench_analysis_sync(job_id: str, content: bytes, model: str, fps: float, threshold: float):
    """Save video file and run DeepfakeBench analysis in background thread (synchronous for ThreadPoolExecutor)"""
    try:
        # Create job directory
        job_dir = DATA_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # Update progress - saving file
        jobs[job_id].update({
            "progress": 5,
            "stage": "Saving file...",
            "message": "Writing video to disk"
        })
        
        # Save input video
        input_path = job_dir / "input.mp4"
        with open(input_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Saved video file for job {job_id}, starting analysis")
        
        # Now run the analysis (synchronous call since we're already in a thread)
        run_deepfakebench_analysis(job_id, str(input_path), model, fps, threshold)
        
    except Exception as e:
        logger.error(f"Failed to save/analyze video for job {job_id}: {e}")
        jobs[job_id].update({
            "status": "error",
            "message": f"Failed to save video: {str(e)}"
        })


def run_deepfakebench_analysis(job_id: str, video_path: str, model: str, fps: float, threshold: float):
    """Run DeepfakeBench analysis in background (synchronous for ThreadPoolExecutor)"""
    try:
        logger.info(f"Starting DeepfakeBench analysis for job {job_id} with model {model}")
        
        # Get job directory for progress file
        job_dir = DATA_DIR / job_id
        
        jobs[job_id].update({
            "progress": 10,
            "stage": "Loading model...",
            "message": f"Initializing {model}"
        })
        
        # Initialize adapter
        adapter = DeepfakeBenchAdapter(model_key=model, device="cuda")
        
        # Progress callback - write to file like TruFor does
        def update_progress(progress, stage, message):
            jobs[job_id].update({
                "progress": progress,
                "stage": stage,
                "message": message
            })
            # Write to progress.json file for polling
            progress_file = job_dir / "progress.json"
            try:
                with open(progress_file, 'w') as f:
                    json.dump({
                        "progress": progress,
                        "stage": stage,
                        "message": message
                    }, f)
                logger.info(f"📊 Progress updated: {progress}% - {stage} - {message}")
            except Exception as e:
                logger.warning(f"Failed to write progress file: {e}")
        
        # Initial progress update
        update_progress(30, "Analyzing video...", "Starting frame analysis")
        
        # Run analysis with progress callback
        result = adapter.analyze_video(video_path, fps=fps, threshold=threshold, progress_callback=update_progress)

        if result["success"]:
            update_progress(95, "Generating report...", "Finalizing results")

            # Save timeline.json for PDF report generation
            try:
                timeline_data = {
                    "summary": {
                        "total_frames": result.get("total_frames", 0),
                        "suspicious_frames": sum(1 for s in result.get("frame_scores", []) if s.get("probability", 0) >= threshold),
                        "suspicious_segments": len(result.get("suspicious_segments", [])),
                        "average_score": result.get("average_score", 0),
                        "max_score": result.get("overall_score", 0)
                    },
                    "frame_scores": result.get("frame_scores", []),
                    "segments": [
                        {
                            "start_time": seg["start"],
                            "end_time": seg["end"],
                            "duration": seg["duration"],
                            "avg_score": seg["peak_score"],
                            "frame_count": int(seg["duration"] * fps)
                        }
                        for seg in result.get("suspicious_segments", [])
                    ]
                }

                timeline_path = job_dir / "timeline.json"
                with open(timeline_path, 'w') as f:
                    json.dump(timeline_data, f, indent=2)
                logger.info(f"Saved timeline.json for job {job_id}")
            except Exception as e:
                logger.warning(f"Failed to save timeline.json for job {job_id}: {e}")

            # Financial risk assessment (shared playbook; fake_prob = overall score)
            result["fake_prob"] = result.get("overall_score", 0)
            attach_risk(result)

            jobs[job_id].update({
                "status": "completed",
                "progress": 100,
                "stage": "Complete",
                "message": "Analysis finished",
                "result": result
            })

            # Update history with result
            history_manager.update_job_status(
                job_id=job_id,
                status="completed",
                result={
                    # Core verdict and scores
                    "verdict": result.get("verdict", "unknown"),
                    "score": result.get("overall_score", 0),          # Overall detection score
                    "average_score": result.get("average_score", 0),   # Average frame score
                    "confidence": result.get("confidence", 0),         # Confidence level
                    "fake_prob": result.get("overall_score", 0),
                    "risk_level": result.get("risk_level", "unknown"),
                    "recommended_actions": result.get("recommended_actions", []),

                    # Model information
                    "model": result.get("model", model),
                    "model_name": result.get("model_name", model),

                    # Analysis parameters
                    "fps": fps,
                    "threshold": threshold,
                    "total_frames": result.get("total_frames", 0),

                    # Segment information
                    "suspicious_segments": len(result.get("suspicious_segments", [])),
                    "suspicious_frames": sum(1 for s in result.get("frame_scores", []) if s.get("probability", 0) >= threshold)
                }
            )

            update_progress(100, "Complete", "Analysis finished")
            logger.info(f"Job {job_id} completed successfully")
        else:
            error_msg = result.get("error", "Analysis failed")
            jobs[job_id].update({
                "status": "error",
                "message": error_msg
            })

            # Update history with error
            history_manager.update_job_status(
                job_id=job_id,
                status="failed",
                error=error_msg
            )

    except Exception as e:
        logger.error(f"DeepfakeBench analysis failed for job {job_id}: {e}")
        import traceback
        traceback.print_exc()

        error_msg = f"Analysis failed: {str(e)}"
        jobs[job_id].update({
            "status": "error",
            "message": error_msg
        })

        # Update history with error
        history_manager.update_job_status(
            job_id=job_id,
            status="failed",
            error=error_msg
        )


@app.get("/api/deepfakebench/jobs/{job_id}")
async def get_deepfakebench_job(job_id: str):
    """Get DeepfakeBench job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # Check for progress updates from progress.json file (like TruFor does)
    job_dir = DATA_DIR / job_id
    progress_file = job_dir / "progress.json"
    
    if progress_file.exists():
        try:
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
                job.update({
                    "progress": progress_data.get("progress", job.get("progress", 0)),
                    "message": progress_data.get("message", job.get("message", "")),
                    "stage": progress_data.get("stage", job.get("stage", "processing"))
                })
                logger.info(f"📨 Sending progress to frontend: {job.get('progress')}% - {job.get('stage')} - {job.get('message')}")
        except Exception as e:
            logger.warning(f"Failed to read progress file: {e}")
    else:
        logger.debug(f"Progress file not found for job {job_id}")
    
    return JSONResponse(content=job)


@app.post("/api/deepfakebench/jobs/{job_id}/extract-keyframe")
async def extract_keyframe(job_id: str, timestamp: float = 0.0):
    """Extract a keyframe at the specified timestamp"""
    import cv2
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get video path
    job_dir = DATA_DIR / job_id
    video_path = job_dir / "input.mp4"
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    try:
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Failed to open video")
        
        # Get video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = total_frames / video_fps if video_fps > 0 else 0
        
        # AGGRESSIVE boundary handling: if timestamp is in last 40% of video, use middle region instead
        # This is because many videos have corrupted frames near the end
        if timestamp > video_duration * 0.6:
            # Map to safe middle region (30% of video duration)
            fallback_timestamp = video_duration * 0.35
            logger.warning(f"⚠️ Timestamp {timestamp:.2f}s is in potentially corrupted end region (>{video_duration*0.6:.2f}s), using fallback at {fallback_timestamp:.2f}s")
            timestamp = fallback_timestamp
        
        # Calculate frame number
        frame_number = int(timestamp * video_fps)
        
        # Ensure frame_number is within safe range (use only first 70% of frames to avoid corruption)
        safe_max_frame = max(0, int(total_frames * 0.7))
        if frame_number > safe_max_frame:
            frame_number = safe_max_frame
            logger.warning(f"⚠️ Frame {int(timestamp * video_fps)} exceeds safe range, capped to frame {safe_max_frame} (70% of video)")
        
        frame_number = max(0, frame_number)
        
        # Seek to frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # Read frame with multiple retries
        ret, frame = cap.read()
        
        # If failed, try multiple previous frames (important for video end)
        retry_attempts = 15  # Try up to 15 frames back
        attempt = 0
        while not ret and attempt < retry_attempts and frame_number - attempt > 0:
            attempt += 1
            retry_frame = frame_number - attempt
            logger.warning(f"Failed to read frame {frame_number - attempt + 1}, trying frame {retry_frame}")
            cap.set(cv2.CAP_PROP_POS_FRAMES, retry_frame)
            ret, frame = cap.read()
        
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=500, detail=f"Failed to extract frame at {timestamp:.2f}s (tried frames {frame_number} to {max(0, frame_number - retry_attempts)})")
        
        # Create keyframes directory
        keyframes_dir = job_dir / "keyframes"
        keyframes_dir.mkdir(exist_ok=True)
        
        # Generate filename based on timestamp
        keyframe_filename = f"keyframe_{timestamp:.2f}s.jpg"
        keyframe_path = keyframes_dir / keyframe_filename
        
        # Save keyframe
        cv2.imwrite(str(keyframe_path), frame)
        
        logger.info(f"Extracted keyframe for job {job_id} at {timestamp:.2f}s -> {keyframe_filename}")
        
        return JSONResponse(content={
            "success": True,
            "keyframe_path": f"keyframes/{keyframe_filename}",
            "timestamp": timestamp
        })
        
    except Exception as e:
        logger.error(f"Failed to extract keyframe: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract keyframe: {str(e)}")


# =============================================================================
# Audio Spoof (Voice Deepfake) API Endpoints
# =============================================================================

def _get_audio_adapter():
    """Lazily initialize the audio spoof adapter (loads ~380MB model once)."""
    global audio_adapter
    if audio_adapter is None:
        audio_adapter = AudioSpoofAdapter(
            model_dir=os.getenv("AUDIO_MODEL_PATH", "models/audio_dhwani")
        )
        logger.info("Audio spoof adapter initialized successfully")
    return audio_adapter


@app.get("/api/audio/models")
async def get_audio_models():
    """Get audio spoof model info and availability (public)."""
    audio_path = Path("models/audio_dhwani/best_model.onnx")
    return JSONResponse(content={
        "models": [{
            "key": "dhwani-spoof",
            "name": "Dhwani Spoof Detector (multilingual: en/hi/ta/te/ml)",
            "speed": "Fast",
            "accuracy": "High",
            "available": audio_path.exists()
        }]
    })


@app.post("/api/audio/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Analyze an audio clip for voice spoofing / AI-generated speech
    (requires authentication). Runs inline; typical CPU time is seconds.
    """
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. "
                   "Allowed: WAV, MP3, OGG, FLAC, M4A, AAC, WebM audio"
        )

    content = await file.read()
    if len(content) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {len(content)/(1024*1024):.1f}MB. Maximum: 50MB"
        )

    timestamp = int(time.time())
    file_hash = hashlib.sha256(content).hexdigest()[:12]
    job_id = f"aud_{file_hash}_{timestamp}"
    logger.info(f"User {user['username']} audio analysis: {file.filename} ({len(content)} bytes) -> {job_id}")

    history_manager.create_job_metadata(
        job_id=job_id,
        username=user["username"],
        filename=file.filename,
        detection_type="audio",
        model="dhwani-spoof"
    )

    try:
        adapter = _get_audio_adapter()
    except Exception as e:
        logger.error(f"Audio model unavailable: {e}")
        history_manager.update_job_status(job_id=job_id, status="failed",
                                          error="Audio model unavailable")
        raise HTTPException(status_code=503, detail="Audio model unavailable")

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor, adapter.analyze, content, file.filename or "audio"
    )

    if not result.get("success"):
        history_manager.update_job_status(
            job_id=job_id, status="failed",
            error=result.get("error", "Analysis failed")
        )
        raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))

    # Persist input + chunk scores for reports/evidence
    job_dir = DATA_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    with open(job_dir / "input_audio", "wb") as f:
        f.write(content)
    with open(job_dir / "audio_scores.json", "w") as f:
        json.dump(result.get("chunks", []), f, indent=2)

    attach_risk(result)  # financial risk + response playbook (before history)
    history_manager.update_job_status(
        job_id=job_id,
        status="completed",
        result={
            "verdict": result.get("verdict", "unknown"),
            "score": result.get("fake_prob", 0),
            "fake_prob": result.get("fake_prob", 0),
            "confidence": result.get("confidence", 0),
            "duration_sec": result.get("duration_sec", 0),
            "num_chunks": result.get("num_chunks", 0),
            "model": result.get("model", "dhwani-spoof"),
            "risk_level": result.get("risk_level", "unknown"),
            "recommended_actions": result.get("recommended_actions", []),
        }
    )

    result["job_id"] = job_id
    return JSONResponse(content=result)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)