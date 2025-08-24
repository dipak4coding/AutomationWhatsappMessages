@echo off
REM WhatsApp Automation - Manual Executable Builder
REM Double-click this file to build WhatsAppAutomation.exe

echo.
echo =========================================================
echo          WhatsApp Automation - Executable Builder
echo =========================================================
echo.

REM Change to script directory
cd /d "%~dp0"
echo Current directory: %CD%

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check if we're in the right directory
if not exist "WhatsAppAutomation_Portable.py" (
    echo ERROR: WhatsAppAutomation_Portable.py not found
    echo Please run this script from the WhatsAppAutomation_Deploy directory
    pause
    exit /b 1
)

echo.
echo Step 1: Cleaning old build files...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo Build files cleaned.

echo.
echo Step 2: Installing/updating dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: requirements.txt not found, installing basic dependencies
    pip install pyinstaller==6.15.0 selenium pandas openpyxl webdriver-manager requests
)

echo.
echo Step 3: Building executable...
echo This may take 2-3 minutes, please wait...
python -m PyInstaller --onefile --console --name WhatsAppAutomation --clean WhatsAppAutomation_Portable.py

REM Check if build was successful
if exist "dist\WhatsAppAutomation.exe" (
    echo.
    echo =========================================================
    echo                   BUILD SUCCESSFUL!
    echo =========================================================
    echo.
    echo Your executable is ready:
    echo Location: %CD%\dist\WhatsAppAutomation.exe
    echo.
    dir "dist\WhatsAppAutomation.exe"
    echo.
    echo To test your executable:
    echo 1. Go to the dist folder
    echo 2. Copy WhatsAppAutomation.exe to a new location
    echo 3. Copy app_config.json and template/data folders
    echo 4. Run: WhatsAppAutomation.exe shs
    echo.
    
    REM Ask if user wants to test now
    set /p test="Do you want to test the executable now? (y/n): "
    if /i "%test%"=="y" (
        echo.
        echo Testing executable...
        cd dist
        WhatsAppAutomation.exe --help
        cd ..
    )
    
) else (
    echo.
    echo =========================================================
    echo                   BUILD FAILED!
    echo =========================================================
    echo.
    echo The executable was not created. Possible solutions:
    echo.
    echo 1. Try running: python fix_pyinstaller.py
    echo 2. Check if antivirus is blocking PyInstaller
    echo 3. Run this script as Administrator
    echo 4. Use Python 3.11 or 3.12 instead of 3.13
    echo.
    echo Alternative: Use the Python version directly
    echo Run: python start_automation.py shs
    echo.
)

echo.
echo Press any key to exit...
pause >nul