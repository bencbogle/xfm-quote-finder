#!/usr/bin/env python3
"""
Build script for Railway deployment.
Builds the frontend and copies it to the dist directory.
"""

import subprocess
import os
import shutil
from pathlib import Path

def main():
    print("🔨 Building XFM Quote Finder for Railway...")
    
    # Build frontend
    print("📦 Building React frontend...")
    result = subprocess.run(["npm", "run", "build"], cwd=".")
    if result.returncode != 0:
        print("❌ Frontend build failed")
        exit(1)
    
    # Create dist directory if it doesn't exist
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Copy frontend build to dist
    frontend_dist = Path("src/dist")
    if frontend_dist.exists():
        print("📁 Copying frontend build to dist...")
        for item in frontend_dist.iterdir():
            if item.is_file():
                shutil.copy2(item, dist_dir)
            else:
                shutil.copytree(item, dist_dir / item.name, dirs_exist_ok=True)
    
    print("✅ Build complete!")

if __name__ == "__main__":
    main()
