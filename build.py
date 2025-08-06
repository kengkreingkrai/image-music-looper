#!/usr/bin/env python3
"""
Build script for Image Music Looper
Creates executable file using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """Install required packages for building"""
    print("📦 Installing build requirements...")
    
    # List of required packages
    requirements = [
        "pyinstaller",
        "pillow",
        "tkinter"  # Usually comes with Python, but just in case
    ]
    
    for package in requirements:
        try:
            print(f"   Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    print("   ✅ All requirements installed successfully!")
    return True

def create_spec_file():
    """Create PyInstaller spec file for better control"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageMusicLooper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # Add icon path here if you have one
)
'''
    
    with open('ImageMusicLooper.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("📝 Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Create spec file first
        create_spec_file()
        
        # Build using spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "ImageMusicLooper.spec"
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Build completed successfully!")
            return True
        else:
            print(f"   ❌ Build failed:")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Build error: {e}")
        return False

def organize_files():
    """Organize built files"""
    print("📁 Organizing files...")
    
    # Create dist directory if it doesn't exist
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("   ❌ Dist directory not found!")
        return False
    
    # Create release directory
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Copy executable
    exe_path = dist_dir / "ImageMusicLooper.exe"
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / "ImageMusicLooper.exe")
        print(f"   ✅ Copied executable to release/")
    else:
        print("   ❌ Executable not found!")
        return False
    
    # Create README for release
    readme_content = """# Image Music Looper

## วิธีใช้งาน

1. ดับเบิลคลิกที่ไฟล์ ImageMusicLooper.exe เพื่อเรียกใช้โปรแกรม
2. เลือกไฟล์ภาพและไฟล์เสียงที่ต้องการ
3. ตั้งค่าความยาววิดีโอและอัตราส่วนภาพ
4. คลิก "เริ่มสร้างวิดีโอ" เพื่อประมวลผล

## ข้อกำหนดระบบ

- Windows 10 ขึ้นไป
- RAM อย่างน้อย 4GB
- พื้นที่ว่างในฮาร์ดดิสก์อย่างน้อย 1GB

## หมายเหตุ

- การประมวลผลอาจใช้เวลานานขึ้นอยู่กับความยาววิดีโอและขนาดไฟล์
- รองรับไฟล์ภาพ: JPG, PNG, BMP
- รองรับไฟล์เสียง: MP3, WAV, M4A, FLAC
"""
    
    with open(release_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✅ Created README.txt")
    return True

def get_file_size(file_path):
    """Get file size in MB"""
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb

def main():
    """Main build process"""
    print("🚀 Starting Image Music Looper build process...")
    print("=" * 50)
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found! Please run this script from the project directory.")
        return 1
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements!")
        return 1
    
    # Build executable
    if not build_executable():
        print("❌ Failed to build executable!")
        return 1
    
    # Organize files
    if not organize_files():
        print("❌ Failed to organize files!")
        return 1
    
    # Show results
    print("=" * 50)
    print("🎉 Build completed successfully!")
    
    exe_path = Path("release/ImageMusicLooper.exe")
    if exe_path.exists():
        size_mb = get_file_size(exe_path)
        print(f"📦 Executable: {exe_path}")
        print(f"📏 Size: {size_mb:.1f} MB")
    
    print("\n📁 Files created:")
    print("   - release/ImageMusicLooper.exe")
    print("   - release/README.txt")
    
    print("\n✨ Ready for distribution!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
