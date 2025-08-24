#!/usr/bin/env python3
"""
Simple Chrome Manager - Guaranteed to work
Falls back to webdriver-manager if custom manager fails
"""

import logging

def get_chromedriver_path():
    """Get ChromeDriver path using the most reliable method."""
    
    # Method 1: Try webdriver-manager first (most reliable)
    try:
        print("🔄 Trying webdriver-manager...")
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver found: {driver_path}")
        return driver_path
    except ImportError:
        print("❌ webdriver-manager not installed")
        print("Installing webdriver-manager...")
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "webdriver-manager"])
            from webdriver_manager.chrome import ChromeDriverManager
            driver_path = ChromeDriverManager().install()
            print(f"✅ ChromeDriver installed: {driver_path}")
            return driver_path
        except Exception as e:
            print(f"❌ Failed to install webdriver-manager: {e}")
    except Exception as e:
        print(f"❌ webdriver-manager failed: {e}")
    
    # Method 2: Try custom chrome_driver_manager
    try:
        print("🔄 Trying custom chrome manager...")
        from chrome_driver_manager import get_chromedriver_path as custom_get_chromedriver
        driver_path = custom_get_chromedriver()
        print(f"✅ Custom ChromeDriver found: {driver_path}")
        return driver_path
    except Exception as e:
        print(f"❌ Custom chrome manager failed: {e}")
    
    # Method 3: Manual ChromeDriver check
    import os
    import platform
    
    possible_paths = []
    if platform.system().lower() == "windows":
        possible_paths = [
            "chromedriver.exe",
            "C:\\chromedriver.exe", 
            os.path.expanduser("~\\chromedriver.exe"),
            "C:\\Windows\\chromedriver.exe"
        ]
    else:
        possible_paths = [
            "chromedriver",
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver",
            os.path.expanduser("~/chromedriver")
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found existing ChromeDriver: {path}")
            return path
    
    # If all methods fail
    error_msg = """
❌ ChromeDriver not found with any method!

SOLUTIONS:
1. Install webdriver-manager: pip install webdriver-manager
2. Download ChromeDriver manually from: https://chromedriver.chromium.org/
3. Install Chrome browser if not installed

Run this to fix:
python install_chrome_dependencies.py
"""
    print(error_msg)
    raise RuntimeError("ChromeDriver not available")

if __name__ == "__main__":
    try:
        path = get_chromedriver_path()
        print(f"\n🎉 SUCCESS: ChromeDriver is available at: {path}")
    except Exception as e:
        print(f"\n💥 FAILED: {e}")