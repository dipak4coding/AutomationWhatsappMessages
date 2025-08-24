@echo off
REM Quick Build - Just build the executable, no fancy stuff

echo Building WhatsAppAutomation.exe...
cd /d "%~dp0"

REM Simple build command
pyinstaller --onefile --clean WhatsAppAutomation_Portable.py

if exist "dist\WhatsAppAutomation_Portable.exe" (
    echo SUCCESS: Executable created as dist\WhatsAppAutomation_Portable.exe
    rename "dist\WhatsAppAutomation_Portable.exe" "WhatsAppAutomation.exe"
    echo Renamed to: dist\WhatsAppAutomation.exe
) else (
    echo FAILED: Try running build_executable.bat instead
)

pause