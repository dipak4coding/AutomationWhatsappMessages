#!/usr/bin/env python3
"""
Install Chrome Dependencies Script
This script ensures all Chrome-related dependencies are properly installed
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status."""
    try:
        print(f"🔄 {description}...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"💥 {description} - Exception: {e}")
        return False

def main():
    print("🚀 Installing Chrome Dependencies for WhatsApp Automation")
    print("=" * 60)
    
    # Required packages for ChromeDriver management
    packages = [
        "webdriver-manager",
        "requests",
        "selenium"
    ]
    
    success_count = 0
    
    for package in packages:
        if run_command(f"pip install {package}", f"Installing {package}"):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Installation Summary: {success_count}/{len(packages)} packages installed")
    
    if success_count == len(packages):
        print("🎉 All dependencies installed successfully!")
        print("\nNow test ChromeDriver:")
        print("python test_chrome_driver.py")
        print("\nOr run automation:")
        print("python start_automation.py shs")
    else:
        print("⚠️ Some packages failed to install")
        print("Try running as administrator or check your internet connection")

if __name__ == "__main__":
    main()