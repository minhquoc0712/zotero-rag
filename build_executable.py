#!/usr/bin/env python3
"""
Local build script for creating standalone executables
Run this before pushing to CI/CD to test the build locally
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous builds...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Removed {dir_name}/")
            except Exception as e:
                print(f"Warning: Could not remove {dir_name}: {e}")
        else:
            print(f"{dir_name}/ does not exist, skipping")
    return True

def install_dependencies():
    """Install required dependencies for building."""
    print("📦 Installing build dependencies...")
    dependencies = [
        "pyinstaller",
        "sentence-transformers",
        "faiss-cpu", 
        "PyPDF2",
        "scikit-learn",
        "numpy"
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        if not run_command(f"{sys.executable} -m pip install {dep}"):
            print(f"Failed to install {dep}")
            return False
    return True

def build_executable():
    """Build the executable using PyInstaller."""
    print("🏗️  Building executable...")
    
    # Use the spec file if it exists, otherwise use direct command
    if os.path.exists("zotero-rag.spec"):
        cmd = f"{sys.executable} -m PyInstaller zotero-rag.spec"
    else:
        # Fallback command
        cmd = f"{sys.executable} -m PyInstaller --onefile --name=zotero-rag --console fast_pdf_opener.py"
    
    return run_command(cmd)

def test_executable():
    """Test the built executable."""
    print("🧪 Testing executable...")
    
    system = platform.system().lower()
    if system == "windows":
        exe_path = "./dist/zotero-rag.exe"
    else:
        exe_path = "./dist/zotero-rag"
        # Make executable on Unix systems
        if os.path.exists(exe_path):
            os.chmod(exe_path, 0o755)
    
    if not os.path.exists(exe_path):
        print(f"Executable not found at {exe_path}")
        return False
    
    # Test help command
    if not run_command(f"{exe_path} --help"):
        print("Help command failed")
        return False
    
    print(f"✅ Executable built successfully at {exe_path}")
    
    # Show file size
    file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
    print(f"📊 Executable size: {file_size:.1f} MB")
    
    return True

def main():
    """Main build process."""
    print("🚀 Starting local executable build...")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    
    steps = [
        ("Clean build", clean_build),
        ("Install dependencies", install_dependencies),
        ("Build executable", build_executable),
        ("Test executable", test_executable),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*50}")
        print(f"Step: {step_name}")
        print('='*50)
        
        try:
            if not step_func():
                print(f"❌ Failed at step: {step_name}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Exception in step {step_name}: {e}")
            sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the executable in ./dist/")
    print("2. If it works, commit and push to trigger CI/CD")
    print("3. Create a GitHub release to distribute binaries")

if __name__ == "__main__":
    main() 