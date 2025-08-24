#!/usr/bin/env python3
"""
Cross-platform Chrome Driver Manager
Automatically detects Chrome version and downloads matching ChromeDriver
Works on Windows, Mac, and Linux
"""

import subprocess
import requests
import zipfile
import os
import platform
import tempfile
import logging
from pathlib import Path

# Setup basic logging (no dependency on logging_manager)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_chrome_version():
    """Get installed Chrome version across platforms."""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Try multiple Windows Chrome detection methods
            try:
                import winreg
                # Method 1: Registry key
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                return version
            except:
                # Method 2: Chrome executable version
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
                ]
                
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        result = subprocess.run([chrome_path, "--version"], 
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            return result.stdout.strip().split()[-1]
        
        elif system == "darwin":  # macOS
            cmd = 'defaults read "/Applications/Google Chrome.app/Contents/Info.plist" CFBundleShortVersionString'
            result = subprocess.check_output(cmd, shell=True, text=True)
            return result.strip()
        
        elif system == "linux":
            # Try different Chrome/Chromium commands
            commands = ["google-chrome --version", "chromium-browser --version", "chrome --version"]
            for cmd in commands:
                try:
                    result = subprocess.check_output(cmd.split(), text=True)
                    return result.strip().split()[-1]
                except:
                    continue
                    
    except Exception as e:
        logging.warning(f"Could not detect Chrome version: {e}")
        
    return None


def get_chromedriver_download_info(chrome_version):
    """Get ChromeDriver download URL for given Chrome version."""
    if not chrome_version:
        raise RuntimeError("Chrome version not detected")
        
    chrome_major = chrome_version.split('.')[0]
    
    try:
        # Get latest ChromeDriver version for Chrome major version
        response = requests.get(
            "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        driver_version = data["milestones"].get(str(chrome_major), {}).get("version")
        if not driver_version:
            raise RuntimeError(f"No ChromeDriver found for Chrome {chrome_major}")
            
    except Exception as e:
        logging.error(f"Could not fetch ChromeDriver version: {e}")
        raise RuntimeError(f"Could not fetch latest driver for Chrome {chrome_major}: {e}")
    
    # Determine platform
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        platform_name = "win64" if "64" in machine or machine in ["x86_64", "amd64"] else "win32"
    elif system == "darwin":
        platform_name = "mac-arm64" if machine == "arm64" else "mac-x64"
    elif system == "linux":
        platform_name = "linux64"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    
    # Build download URL
    url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{driver_version}/{platform_name}/chromedriver-{platform_name}.zip"
    
    return url, driver_version, platform_name


def get_chromedriver_path():
    """Download and setup ChromeDriver, return path to executable."""
    try:
        # 1. Detect Chrome version
        chrome_version = get_chrome_version()
        logging.info(f"Detected Chrome version: {chrome_version}")
        print(f"Detected Chrome version: {chrome_version}")
        
        # 2. Get download info
        url, driver_version, platform_name = get_chromedriver_download_info(chrome_version)
        logging.info(f"ChromeDriver version: {driver_version}")
        logging.info(f"Platform: {platform_name}")
        logging.info(f"Download URL: {url}")
        print(f"ChromeDriver version: {driver_version} for platform: {platform_name}")
        
        # 3. Setup paths
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, "chromedriver.zip")
        extract_dir = os.path.join(temp_dir, "chromedriver_extract")
        
        # ChromeDriver executable name
        exe_name = "chromedriver.exe" if platform.system().lower() == "windows" else "chromedriver"
        driver_path = os.path.join(extract_dir, f"chromedriver-{platform_name}", exe_name)
        
        # 4. Check if already exists and is correct version
        if os.path.exists(driver_path):
            try:
                result = subprocess.run([driver_path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if driver_version in result.stdout:
                    logging.info(f"ChromeDriver {driver_version} already exists")
                    print(f"ChromeDriver {driver_version} already exists at: {driver_path}")
                    return driver_path
            except:
                pass
        
        # 5. Download ChromeDriver
        print(f"Downloading ChromeDriver {driver_version}...")
        logging.info(f"Downloading from: {url}")
        
        Path(extract_dir).mkdir(exist_ok=True, parents=True)
        
        with requests.get(url, stream=True, timeout=30) as response:
            response.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # 6. Extract
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            zip_file.extractall(extract_dir)
        
        # 7. Verify extraction
        if not os.path.exists(driver_path):
            raise RuntimeError(f"ChromeDriver executable not found at: {driver_path}")
        
        # 8. Make executable (Unix-like systems)
        if platform.system().lower() != "windows":
            os.chmod(driver_path, 0o755)
        
        # 9. Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        logging.info(f"ChromeDriver successfully installed: {driver_path}")
        print(f"ChromeDriver successfully installed: {driver_path}")
        return driver_path
        
    except Exception as e:
        error_msg = f"Failed to setup ChromeDriver: {e}"
        logging.error(error_msg)
        print(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)


if __name__ == "__main__":
    # Test the Chrome driver manager
    try:
        driver_path = get_chromedriver_path()
        print(f"SUCCESS: ChromeDriver available at: {driver_path}")
    except Exception as e:
        print(f"FAILED: {e}")
