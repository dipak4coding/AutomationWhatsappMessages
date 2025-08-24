#!/usr/bin/env python3
"""
Fix Chrome Data Directory Script
Resolves Chrome user data directory permission issues on Windows/Mac/Linux
"""

import os
import sys
import shutil
import platform
import subprocess
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


def get_app_directory():
    """Get the application directory."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as Python script
        return os.path.dirname(os.path.abspath(__file__))


def clean_chrome_processes():
    """Kill any running Chrome processes."""
    print_step(1, "Closing Chrome Processes")
    
    try:
        if platform.system().lower() == "windows":
            commands = [
                "taskkill /f /im chrome.exe /t",
                "taskkill /f /im chromedriver.exe /t"
            ]
        else:
            commands = [
                "pkill -f chrome",
                "pkill -f chromedriver"
            ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ {cmd}")
                else:
                    print(f"ℹ️  {cmd} - No processes found")
            except Exception as e:
                print(f"⚠️  {cmd} - {e}")
                
    except Exception as e:
        print(f"❌ Failed to clean processes: {e}")


def fix_directory_permissions(directory_path):
    """Fix directory permissions for Chrome."""
    try:
        abs_path = os.path.abspath(directory_path)
        
        # Remove directory if it exists (fresh start)
        if os.path.exists(abs_path):
            print(f"🗑️  Removing existing directory: {abs_path}")
            shutil.rmtree(abs_path, ignore_errors=True)
        
        # Create directory with proper structure
        print(f"📁 Creating directory: {abs_path}")
        Path(abs_path).mkdir(parents=True, exist_ok=True)
        
        # Create essential Chrome subdirectories
        essential_dirs = [
            "Default",
            "Default/Local Storage",
            "Default/Session Storage", 
            "Default/IndexedDB",
            "Default/Cache",
            "Default/Extensions",
            "Default/Web Applications",
            "ShaderCache",
            "SwReporter"
        ]
        
        for subdir in essential_dirs:
            subdir_path = os.path.join(abs_path, subdir)
            Path(subdir_path).mkdir(parents=True, exist_ok=True)
        
        # Set permissions based on platform
        if platform.system().lower() == "windows":
            try:
                # Reset and set full control for current user
                cmd1 = f'icacls "{abs_path}" /reset /T'
                cmd2 = f'icacls "{abs_path}" /grant %username%:F /T'
                
                subprocess.run(cmd1, shell=True, capture_output=True, text=True)
                result = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Windows permissions set for: {abs_path}")
                else:
                    print(f"⚠️  Permission command failed: {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Could not set Windows permissions: {e}")
        else:
            try:
                import stat
                # Set full permissions for owner, read+execute for others
                os.chmod(abs_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                print(f"✅ Unix permissions set for: {abs_path}")
            except Exception as e:
                print(f"❌ Could not set Unix permissions: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix permissions for {directory_path}: {e}")
        return False


def create_test_chrome_instance(user_data_dir):
    """Test Chrome with the fixed directory."""
    print_step(3, "Testing Chrome Data Directory")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        # Try to import our chrome manager
        try:
            from simple_chrome_manager import get_chromedriver_path
            chromedriver_path = get_chromedriver_path()
        except ImportError:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                chromedriver_path = ChromeDriverManager().install()
            except ImportError:
                print("❌ No ChromeDriver manager available")
                return False
        
        # Configure Chrome with fixed directory
        options = Options()
        abs_user_data_dir = os.path.abspath(user_data_dir)
        
        options.add_argument(f"--user-data-dir={abs_user_data_dir}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")  # Run in headless for test
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        print(f"🔄 Testing Chrome with data directory: {abs_user_data_dir}")
        
        # Initialize Chrome
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        # Test basic navigation
        driver.get("https://www.google.com")
        title = driver.title
        
        # Close driver
        driver.quit()
        
        print(f"✅ Chrome test successful! Page title: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Chrome test failed: {e}")
        return False


def main():
    """Main fix routine."""
    print_header("Chrome Data Directory Fix Script")
    print("This script will fix Chrome user data directory permission issues")
    
    # Get application directory
    app_dir = get_app_directory()
    print(f"📁 Application directory: {app_dir}")
    
    # Define user data directories
    user_data_dirs = [
        os.path.join(app_dir, "user_data", "profile_shs"),
        os.path.join(app_dir, "user_data", "profile_sud")
    ]
    
    try:
        # Step 1: Clean Chrome processes
        clean_chrome_processes()
        
        # Step 2: Fix directories
        print_step(2, "Fixing User Data Directories")
        
        success_count = 0
        for user_data_dir in user_data_dirs:
            print(f"\n🔧 Fixing: {user_data_dir}")
            if fix_directory_permissions(user_data_dir):
                success_count += 1
                print(f"✅ Fixed: {user_data_dir}")
            else:
                print(f"❌ Failed: {user_data_dir}")
        
        if success_count == 0:
            print("\n❌ FAILED: Could not fix any directories")
            return False
        
        # Step 3: Test one of the fixed directories
        test_dir = user_data_dirs[0]  # Test the first one
        if create_test_chrome_instance(test_dir):
            print(f"\n🎉 SUCCESS: Chrome data directories fixed!")
            print(f"✅ {success_count}/{len(user_data_dirs)} directories fixed")
            
            print(f"\n🚀 Now you can run:")
            print(f"   python start_automation.py shs")
            print(f"   python WhatsAppAutomation_Portable.py shs")
            
            return True
        else:
            print(f"\n⚠️  Directories fixed but Chrome test failed")
            print(f"Try running the automation anyway:")
            print(f"   python start_automation.py shs")
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
        print("Chrome data directory should now work correctly.")
    else:
        print("❌ SCRIPT COMPLETED WITH ISSUES")
        print("Manual intervention may be required.")
    print("=" * 60)
    
    input("\nPress Enter to exit...")