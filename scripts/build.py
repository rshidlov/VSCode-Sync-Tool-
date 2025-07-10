#!/usr/bin/env python3
"""
Build script for VSCode Sync Tool
Creates standalone executables for different platforms
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {cmd}")
        print(f"Error: {e.stderr}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    return run_command("pip install -r requirements.txt")

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    return run_command("pip install pyinstaller")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    return run_command("pyinstaller --onefile --name vscode-sync vscode_sync/main.py")

def build_with_spec():
    """Build using the spec file"""
    print("Building with spec file...")
    return run_command("pyinstaller vscode-sync.spec")

def create_dist_folder():
    """Create distribution folder structure"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    dist_name = f"vscode-sync-{system}-{arch}"
    dist_path = Path("dist") / dist_name
    
    # Create dist folder
    dist_path.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    exe_name = "vscode-sync.exe" if system == "windows" else "vscode-sync"
    exe_source = Path("dist") / exe_name
    
    if exe_source.exists():
        shutil.copy2(exe_source, dist_path / exe_name)
        print(f"✓ Copied executable to {dist_path}")
    else:
        print(f"✗ Executable not found at {exe_source}")
        return False
    
    # Copy documentation
    docs = ["README.md", "LICENSE"]
    for doc in docs:
        if Path(doc).exists():
            shutil.copy2(doc, dist_path / doc)
    
    # Create archive
    archive_name = f"{dist_name}.zip"
    shutil.make_archive(str(Path("dist") / dist_name), 'zip', str(dist_path))
    print(f"✓ Created archive: {archive_name}")
    
    return True

def main():
    """Main build process"""
    print("VSCode Sync Tool - Build Script")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher required")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies")
        sys.exit(1)
    
    # Install PyInstaller
    if not install_pyinstaller():
        print("Failed to install PyInstaller")
        sys.exit(1)
    
    # Build executable
    if not build_executable():
        print("Failed to build executable")
        sys.exit(1)
    
    # Create distribution package
    if not create_dist_folder():
        print("Failed to create distribution package")
        sys.exit(1)
    
    print("\n✓ Build completed successfully!")
    print("Executable and distribution package created in 'dist' folder")

if __name__ == "__main__":
    main()
