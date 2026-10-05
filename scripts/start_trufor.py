#!/usr/bin/env python3
"""
Start the deepfake detection service with TruFor model
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Start TruFor model service"""
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Load environment variables
    load_dotenv()
    
    # Set environment variables for TruFor
    os.environ["MODEL_TYPE"] = "trufor"
    os.environ["MODEL_PATH"] = "models/trufor.pth.tar"
    
    # Check if model file exists
    model_path = Path("models/trufor.pth.tar")
    if not model_path.exists():
        print("❌ Error: Model file 'models/trufor.pth.tar' not found")
        print("Please ensure the TruFor model file is in the models/ directory")
        print("See docs/guides/WEIGHTS_DOWNLOAD_GUIDE.md for instructions")
        sys.exit(1)
    
    print("Starting VAJRA Trust Intelligence (Verification & AI-based Judgement for Risk Assessment) with TruFor model")
    print("=" * 60)
    print(f"📁 Model file: {model_path.absolute()}")
    print(f"🌐 Home Page: http://localhost:8000/web/index_main.html")
    print(f"📖 API docs: http://localhost:8000/docs")
    print(f"🖥️  All pages: http://localhost:8000/ (root)")
    print("=" * 60)
    print("⚠️  Note: TruFor model loading may take 10-30 seconds...")
    print("Press Ctrl+C to stop the service")
    print()
    
    try:
        # Start service
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Service stopped")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


