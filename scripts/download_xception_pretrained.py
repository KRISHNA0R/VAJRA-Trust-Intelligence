"""
Download Xception ImageNet pretrained weights for F3Net and other models
"""
import os
import urllib.request
import hashlib
from pathlib import Path

def download_file(url, output_path, expected_md5=None):
    """Download a file from URL to output_path"""
    print(f"Downloading from: {url}")
    print(f"Saving to: {output_path}")
    
    try:
        # Download with progress
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, downloaded * 100 / total_size)
            print(f"\rProgress: {percent:.1f}%", end='')
        
        urllib.request.urlretrieve(url, output_path, show_progress)
        print("\n✅ Download complete!")
        
        # Verify MD5 if provided
        if expected_md5:
            print(f"Verifying MD5 checksum...")
            with open(output_path, 'rb') as f:
                file_md5 = hashlib.md5(f.read()).hexdigest()
            if file_md5 == expected_md5:
                print(f"✅ MD5 verification passed!")
            else:
                print(f"⚠️ MD5 mismatch! Expected: {expected_md5}, Got: {file_md5}")
        
        return True
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False

def main():
    # Define output directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "vendors" / "DeepfakeBench" / "training" / "pretrained"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "xception-b5690688.pth"
    
    if output_file.exists():
        print(f"✅ File already exists: {output_file}")
        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"   File size: {file_size:.2f} MB")
        overwrite = input("Do you want to re-download? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Skipping download.")
            return
    
    print("\n🔍 Attempting to download Xception ImageNet pretrained weights...\n")
    
    # Try multiple sources
    download_sources = [
        {
            "name": "PyTorch Hub (timm mirror)",
            "url": "https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-cadene/xception-b5690688.pth",
            "md5": None
        },
        {
            "name": "Cadene's pretrained models",
            "url": "http://data.lip6.fr/cadene/pretrainedmodels/xception-b5690688.pth",
            "md5": None
        },
        {
            "name": "Alternative Mirror 1",
            "url": "https://download.openmmlab.com/mmclassification/v0/xception/xception_3rdparty-b5690688.pth",
            "md5": None
        }
    ]
    
    success = False
    for i, source in enumerate(download_sources, 1):
        print(f"\n{'='*60}")
        print(f"Source {i}/{len(download_sources)}: {source['name']}")
        print(f"{'='*60}")
        
        if download_file(source['url'], output_file, source.get('md5')):
            success = True
            break
        else:
            print(f"❌ Failed to download from {source['name']}")
            if output_file.exists():
                output_file.unlink()  # Delete partial file
    
    if success:
        print(f"\n✅ SUCCESS! Xception pretrained weights saved to:")
        print(f"   {output_file}")
        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"   File size: {file_size:.2f} MB")
        print(f"\n🎯 You can now use F3Net and other models that require Xception pretrained weights!")
    else:
        print(f"\n❌ All download attempts failed.")
        print(f"\n📝 Manual Download Instructions:")
        print(f"   1. Try downloading from one of these sources manually:")
        for source in download_sources:
            print(f"      - {source['url']}")
        print(f"\n   2. Save the file as: {output_file}")
        print(f"   3. Make sure the file size is approximately 85-95 MB")

if __name__ == "__main__":
    main()

