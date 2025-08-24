#!/usr/bin/env python3
"""
PyInstaller Fix Script for Windows
Automatically fixes common PyInstaller bootloader issues
"""

import os
import sys
import shutil
import subprocess
import platform
import time
from pathlib import Path


def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"🔧 {title}")
    print("=" * 60)


def print_step(step, description):
    """Print formatted step."""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)


def run_command(cmd, description="", timeout=60):
    """Run command and return success status."""
    try:
        if description:
            print(f"⏳ {description}")
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed: {description}")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout: {description}")
        return False
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False


def check_system_info():
    """Check and display system information."""
    print_header("System Information")
    
    print(f"🐍 Python Version: {sys.version}")
    print(f"💻 Platform: {platform.platform()}")
    print(f"🏗️ Architecture: {platform.architecture()}")
    print(f"📁 Current Directory: {os.getcwd()}")
    
    # Check if we're on Windows
    if platform.system().lower() != "windows":
        print("⚠️  WARNING: This script is designed for Windows!")
        return False
    
    return True


def check_pyinstaller():
    """Check PyInstaller installation."""
    print_step(1, "Checking PyInstaller Installation")
    
    try:
        import PyInstaller
        version = PyInstaller.__version__
        print(f"✅ PyInstaller found: version {version}")
        return version
    except ImportError:
        print("❌ PyInstaller not installed")
        return None


def kill_python_processes():
    """Kill any running Python processes."""
    print_step(2, "Killing Python Processes")
    
    commands = [
        "taskkill /f /im python.exe /t",
        "taskkill /f /im pythonw.exe /t"
    ]
    
    for cmd in commands:
        run_command(cmd, f"Running: {cmd}", timeout=10)


def clear_pyinstaller_cache():
    """Clear PyInstaller cache directories."""
    print_step(3, "Clearing PyInstaller Cache")
    
    cache_paths = [
        os.path.expandvars("%LOCALAPPDATA%\\pyinstaller"),
        os.path.expandvars("%USERPROFILE%\\AppData\\Local\\pyinstaller"),
        os.path.expandvars("%TEMP%\\pyinstaller"),
        os.path.expandvars("%TMP%\\pyinstaller")
    ]
    
    for cache_path in cache_paths:
        try:
            if os.path.exists(cache_path):
                shutil.rmtree(cache_path, ignore_errors=True)
                print(f"✅ Cleared: {cache_path}")
            else:
                print(f"ℹ️  Not found: {cache_path}")
        except Exception as e:
            print(f"⚠️  Could not clear {cache_path}: {e}")


def clear_build_files():
    """Clear build files in current directory."""
    print_step(4, "Clearing Build Files")
    
    build_items = ["build", "dist", "*.spec", "__pycache__"]
    
    for item in build_items:
        try:
            if item == "*.spec":
                # Handle spec files
                for spec_file in Path(".").glob("*.spec"):
                    spec_file.unlink()
                    print(f"✅ Removed: {spec_file}")
            elif item == "__pycache__":
                # Handle pycache directories
                for pycache in Path(".").rglob("__pycache__"):
                    shutil.rmtree(pycache, ignore_errors=True)
                    print(f"✅ Removed: {pycache}")
            else:
                # Handle build/dist directories
                if os.path.exists(item):
                    shutil.rmtree(item, ignore_errors=True)
                    print(f"✅ Removed: {item}")
                else:
                    print(f"ℹ️  Not found: {item}")
        except Exception as e:
            print(f"⚠️  Could not remove {item}: {e}")


def reinstall_pyinstaller():
    """Reinstall PyInstaller with force."""
    print_step(5, "Reinstalling PyInstaller")
    
    # Uninstall first
    if run_command("pip uninstall pyinstaller -y", "Uninstalling PyInstaller"):
        time.sleep(2)
    
    # Install fresh
    return run_command(
        "pip install --force-reinstall --no-cache-dir pyinstaller==6.15.0", 
        "Installing PyInstaller 6.15.0"
    )


def try_development_version():
    """Try PyInstaller development version."""
    print_step(6, "Trying Development PyInstaller")
    
    # Uninstall first
    run_command("pip uninstall pyinstaller -y", "Uninstalling PyInstaller")
    
    # Install development version
    return run_command(
        "pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip",
        "Installing Development PyInstaller",
        timeout=120
    )


def test_pyinstaller():
    """Test PyInstaller with a simple script."""
    print_step(7, "Testing PyInstaller")
    
    # Create test script
    test_script = "test_pyinstaller.py"
    test_content = '''
import sys
print("Hello from PyInstaller test!")
print(f"Python version: {sys.version}")
input("Press Enter to exit...")
'''
    
    try:
        with open(test_script, 'w') as f:
            f.write(test_content)
        
        # Test PyInstaller
        success = run_command(
            f"python -m PyInstaller --onefile --console --clean {test_script}",
            "Building test executable",
            timeout=90
        )
        
        # Cleanup
        if os.path.exists(test_script):
            os.remove(test_script)
        
        return success
        
    except Exception as e:
        print(f"💥 Test failed: {e}")
        return False


def build_whatsapp_automation():
    """Try to build the WhatsApp automation executable."""
    print_step(8, "Building WhatsApp Automation")
    
    script_name = "WhatsAppAutomation_Portable.py"
    
    if not os.path.exists(script_name):
        print(f"❌ Script not found: {script_name}")
        return False
    
    return run_command(
        f"python -m PyInstaller --onefile --console --name WhatsAppAutomation --clean {script_name}",
        "Building WhatsApp Automation executable",
        timeout=120
    )


def main():
    """Main fix routine."""
    print_header("PyInstaller Fix Script for Windows")
    print("This script will automatically fix common PyInstaller issues")
    
    # Check system
    if not check_system_info():
        print("❌ System check failed!")
        return False
    
    # Check PyInstaller
    pyinstaller_version = check_pyinstaller()
    
    try:
        # Step 1: Kill processes
        kill_python_processes()
        
        # Step 2: Clear caches
        clear_pyinstaller_cache()
        
        # Step 3: Clear build files
        clear_build_files()
        
        # Step 4: Try reinstalling current version
        if reinstall_pyinstaller():
            # Test if it works now
            if test_pyinstaller():
                print("\n🎉 SUCCESS: PyInstaller fixed with stable version!")
                
                # Try building WhatsApp automation
                if build_whatsapp_automation():
                    print("\n🚀 SUCCESS: WhatsApp Automation executable built successfully!")
                    return True
                else:
                    print("\n⚠️  PyInstaller works but WhatsApp build failed. Check dependencies.")
                    return False
        
        # Step 5: If stable version failed, try development version
        print("\n🔄 Stable version failed. Trying development version...")
        if try_development_version():
            if test_pyinstaller():
                print("\n🎉 SUCCESS: PyInstaller fixed with development version!")
                
                # Try building WhatsApp automation
                if build_whatsapp_automation():
                    print("\n🚀 SUCCESS: WhatsApp Automation executable built successfully!")
                    return True
                else:
                    print("\n⚠️  Development PyInstaller works but WhatsApp build failed.")
                    return False
        
        # If all else fails
        print("\n❌ FAILED: Could not fix PyInstaller")
        print("\n💡 ALTERNATIVE SOLUTION:")
        print("Use the Universal Launcher instead:")
        print("  python start_automation.py shs")
        print("\nThis provides the same functionality without PyInstaller!")
        
        return False
        
    except KeyboardInterrupt:
        print("\n⚠️  Script interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SCRIPT COMPLETED SUCCESSFULLY!")
        print("Your PyInstaller should now work correctly.")
    else:
        print("❌ SCRIPT COMPLETED WITH ISSUES")
        print("Consider using the Universal Launcher as alternative.")
    print("=" * 60)
    
    input("\nPress Enter to exit...")