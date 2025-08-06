@echo off
echo 🔧 Image Music Looper - Fix Dependencies
echo =========================================
echo.

echo 📦 Installing MoviePy...
pip install moviepy
if %errorlevel% neq 0 (
    echo ❌ Failed to install MoviePy
    echo.
    echo 💡 Alternative solutions:
    echo 1. Install FFmpeg from https://ffmpeg.org
    echo 2. Run from Python: python app.py
    echo 3. Rebuild: python build.py
    goto end
)

echo ✅ MoviePy installed successfully!
echo.
echo 🚀 You can now run ImageMusicLooper.exe
echo.

:end
echo.
echo Press any key to exit...
pause >nul
