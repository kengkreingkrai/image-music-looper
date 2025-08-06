@echo off
echo =================================================
echo    Image Music Looper - Build Script
echo =================================================
echo.

echo ๐ ตรวจสอบ Python...
python --version
if errorlevel 1 (
    echo โ Python ไม่พบ! กรุณาติดตั้ง Python ก่อน
    pause
    exit /b 1
)

echo.
echo ๐ฆ ติดตั้ง dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo โ ติดตั้ง dependencies ไม่สำเร็จ!
    pause
    exit /b 1
)

echo.
echo ๐จ เริ่ม build executable...
python build.py
if errorlevel 1 (
    echo โ Build ไม่สำเร็จ!
    pause
    exit /b 1
)

echo.
echo ๐ Build เสร็จสิ้น!
echo ไฟล์ executable อยู่ที่: release\ImageMusicLooper.exe
echo.
pause
