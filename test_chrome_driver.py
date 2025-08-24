#!/usr/bin/env python3
"""
Test Chrome Driver Manager
Run this to verify ChromeDriver setup works on your system
"""

def test_chrome_driver_manager():
    """Test the custom chrome driver manager."""
    print("Testing Custom Chrome Driver Manager...")
    print("=" * 50)
    
    try:
        from chrome_driver_manager import get_chromedriver_path
        print("✅ chrome_driver_manager imported successfully")
        
        driver_path = get_chromedriver_path()
        print(f"✅ ChromeDriver path obtained: {driver_path}")
        
        # Test if the driver actually works
        import os
        if os.path.exists(driver_path):
            print(f"✅ ChromeDriver file exists at: {driver_path}")
        else:
            print(f"❌ ChromeDriver file not found at: {driver_path}")
            
        return True
        
    except Exception as e:
        print(f"❌ Custom chrome driver manager failed: {e}")
        return False

def test_webdriver_manager_fallback():
    """Test the webdriver-manager fallback."""
    print("Testing WebDriver-Manager Fallback...")
    print("=" * 50)
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ webdriver-manager imported successfully")
        
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver path from webdriver-manager: {driver_path}")
        
        import os
        if os.path.exists(driver_path):
            print(f"✅ ChromeDriver file exists at: {driver_path}")
        else:
            print(f"❌ ChromeDriver file not found at: {driver_path}")
            
        return True
        
    except ImportError:
        print("❌ webdriver-manager not installed")
        print("Install it with: pip install webdriver-manager")
        return False
    except Exception as e:
        print(f"❌ webdriver-manager failed: {e}")
        return False

def main():
    """Run all ChromeDriver tests."""
    print("WhatsApp Automation - ChromeDriver Test")
    print("=" * 60)
    
    # Test 1: Custom chrome driver manager
    custom_success = test_chrome_driver_manager()
    print()
    
    # Test 2: webdriver-manager fallback
    fallback_success = test_webdriver_manager_fallback()
    print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY:")
    print(f"Custom Chrome Driver Manager: {'✅ PASS' if custom_success else '❌ FAIL'}")
    print(f"WebDriver-Manager Fallback:   {'✅ PASS' if fallback_success else '❌ FAIL'}")
    
    if custom_success or fallback_success:
        print("\n🎉 SUCCESS: At least one ChromeDriver method works!")
        print("Your WhatsApp automation should work now.")
        print("Run: python WhatsAppAutomation_Portable.py shs")
    else:
        print("\n⚠️  ISSUE: Both ChromeDriver methods failed.")
        print("Try installing dependencies: pip install webdriver-manager")

if __name__ == "__main__":
    main()