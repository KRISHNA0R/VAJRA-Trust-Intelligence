"""
Model Loading Test Script

Run this to verify that models can be loaded successfully.
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_trufor_loading():
    """Test TruFor model loading"""
    print("\n" + "="*60)
    print("Testing TruFor Model")
    print("="*60)
    
    try:
        from app.adapters.trufor_adapter import TruForAdapter
        
        adapter = TruForAdapter()
        
        if adapter.is_available():
            print("✅ TruFor model loaded successfully")
            print(f"   Model path: {adapter.model_path}")
            print(f"   Device: {adapter.device}")
            return True
        else:
            print("❌ TruFor model not available")
            print(f"   Expected path: models/trufor.pth.tar")
            print("\n   📥 To download TruFor model:")
            print("      See docs/TRUFOR_TECHNICAL_GUIDE.md")
            return False
    except Exception as e:
        print(f"❌ TruFor loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_deepfakebench_loading():
    """Test DeepfakeBench model loading"""
    print("\n" + "="*60)
    print("Testing DeepfakeBench Models")
    print("="*60)
    
    try:
        from app.adapters.deepfakebench_adapter import DeepfakeBenchAdapter
        
        adapter = DeepfakeBenchAdapter()
        available_models = adapter.get_available_models()
        
        if len(available_models) > 0:
            print(f"✅ Found {len(available_models)} available models:")
            for model in available_models:
                print(f"   ✓ {model}")
            return True
        else:
            print("❌ No DeepfakeBench models available")
            print("\n   Expected location: vendors/DeepfakeBench/training/weights/")
            print("   Expected files:")
            print("      - xception_best.pth")
            print("      - mesonet_best.pth")
            print("      - f3net_best.pth")
            print("      - etc.")
            print("\n   📥 To download model weights:")
            print("      See WEIGHTS_DOWNLOAD_GUIDE.md")
            return False
    except Exception as e:
        print(f"❌ DeepfakeBench loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_configs():
    """Test model configuration files"""
    print("\n" + "="*60)
    print("Testing Configuration Files")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    
    configs = {
        "Main Config": "configs/config.yaml",
        "Xception Config": "vendors/DeepfakeBench/training/config/detector/xception.yaml",
        "MesoNet Config": "vendors/DeepfakeBench/training/config/detector/mesonet.yaml",
        "F3Net Config": "vendors/DeepfakeBench/training/config/detector/f3net.yaml",
    }
    
    all_exist = True
    for name, config_path in configs.items():
        full_path = project_root / config_path
        if full_path.exists():
            print(f"✅ {name:<20} {config_path}")
        else:
            print(f"⚠️  {name:<20} {config_path} (not found)")
            all_exist = False
    
    return all_exist


def test_dependencies():
    """Test that required dependencies are installed"""
    print("\n" + "="*60)
    print("Testing Dependencies")
    print("="*60)
    
    required_packages = [
        ("torch", "PyTorch"),
        ("torchvision", "TorchVision"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("yaml", "PyYAML"),
        ("numpy", "NumPy"),
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name:<20} installed")
        except ImportError:
            print(f"❌ {name:<20} NOT installed")
            all_installed = False
    
    # Check CUDA
    try:
        import torch
        if torch.cuda.is_available():
            print(f"\n✅ CUDA available")
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print(f"\n⚠️  CUDA not available (will use CPU)")
    except:
        pass
    
    return all_installed


def check_weight_files():
    """Check if weight files exist"""
    print("\n" + "="*60)
    print("Checking Weight Files")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    
    # Check TruFor
    trufor_path = project_root / "models/trufor.pth.tar"
    if trufor_path.exists():
        size_mb = trufor_path.stat().st_size / (1024 * 1024)
        print(f"✅ TruFor weight: {trufor_path.name} ({size_mb:.1f} MB)")
    else:
        print(f"❌ TruFor weight not found: {trufor_path}")
    
    # Check DeepfakeBench weights
    weights_dir = project_root / "vendors" / "DeepfakeBench" / "training" / "weights"
    if weights_dir.exists():
        weight_files = list(weights_dir.glob("*.pth"))
        if weight_files:
            print(f"\n✅ DeepfakeBench weights ({len(weight_files)} files):")
            for weight_file in weight_files:
                size_mb = weight_file.stat().st_size / (1024 * 1024)
                print(f"   - {weight_file.name} ({size_mb:.1f} MB)")
        else:
            print(f"\n⚠️  DeepfakeBench weights directory exists but is empty")
            print(f"   Location: {weights_dir}")
    else:
        print(f"\n❌ DeepfakeBench weights directory not found")
        print(f"   Expected: {weights_dir}")


def main():
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "MODEL LOADING TESTS" + " "*24 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Dependencies", test_dependencies()))
    results.append(("Config Files", test_model_configs()))
    check_weight_files()
    results.append(("TruFor Loading", test_trufor_loading()))
    results.append(("DeepfakeBench Loading", test_deepfakebench_loading()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All models loaded successfully!")
    else:
        print("\n⚠️  Some models failed to load.")
        print("   This is expected if you haven't downloaded model weights yet.")
        print("   See WEIGHTS_DOWNLOAD_GUIDE.md for instructions.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

