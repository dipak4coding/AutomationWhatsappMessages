#!/usr/bin/env python3
"""
Simple executable builder for WhatsApp Automation
Creates standalone .exe (Windows) or executable (Mac/Linux) files
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_executable():
    """Create standalone executable for WhatsApp automation."""
    
    print("WhatsApp Automation - Executable Builder")
    print("=" * 45)
    print(f"Platform: {platform.system()} {platform.machine()}")
    
    # Install PyInstaller if needed
    if not install_pyinstaller():
        return False
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if main script exists
    main_script = os.path.join(current_dir, 'WhatsAppAutomation_Portable.py')
    if not os.path.exists(main_script):
        print(f"❌ Main script not found: {main_script}")
        return False
    
    print(f"Building executable from: {main_script}")
    
    # Build command
    executable_name = 'WhatsAppAutomation'
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # Single executable file
        '--console',                    # Show console window
        '--name', executable_name,      # Name of executable
        '--clean',                      # Clean build
        'WhatsAppAutomation_Portable.py'
    ]
    
    # Add icon if available
    if platform.system() == 'Windows':
        if os.path.exists('app_icon.ico'):
            cmd.extend(['--icon', 'app_icon.ico'])
    elif platform.system() == 'Darwin':  # macOS
        if os.path.exists('app_icon.icns'):
            cmd.extend(['--icon', 'app_icon.icns'])
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Move executable to current directory
        dist_dir = os.path.join(current_dir, 'dist')
        if platform.system() == 'Windows':
            exe_name = f'{executable_name}.exe'
        else:
            exe_name = executable_name
            
        exe_path = os.path.join(dist_dir, exe_name)
        
        if os.path.exists(exe_path):
            # Move to current directory
            new_path = os.path.join(current_dir, exe_name)
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(exe_path, new_path)
            
            # Make executable on Unix systems
            if platform.system() != 'Windows':
                os.chmod(new_path, 0o755)
            
            file_size = os.path.getsize(new_path) / (1024 * 1024)  # MB
            
            print(f"✅ Executable created: {exe_name}")
            print(f"✅ Size: {file_size:.1f} MB")
            print(f"✅ Location: {new_path}")
            
            # Cleanup build directories
            cleanup_dirs = ['build', 'dist', '__pycache__']
            for cleanup_dir in cleanup_dirs:
                cleanup_path = os.path.join(current_dir, cleanup_dir)
                if os.path.exists(cleanup_path):
                    import shutil
                    shutil.rmtree(cleanup_path)
                    print(f"🗑️  Cleaned up: {cleanup_dir}")
            
            # Remove spec file
            spec_file = f'{executable_name}.spec'
            if os.path.exists(spec_file):
                os.remove(spec_file)
                print(f"🗑️  Cleaned up: {spec_file}")
            
            return True
        else:
            print(f"❌ Executable not found at: {exe_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    """Main function."""
    print("Creating standalone executable for WhatsApp Automation...")
    print()
    
    if create_executable():
        print("\n🎉 SUCCESS!")
        print("=" * 30)
        
        if platform.system() == 'Windows':
            exe_name = 'WhatsAppAutomation.exe'
        else:
            exe_name = 'WhatsAppAutomation'
            
        print(f"✅ Executable: {exe_name}")
        print("✅ Ready for distribution!")
        print()
        print("Next steps:")
        print("1. Test the executable on your system")
        print("2. Copy entire folder to target computers")
        print("3. Users can run the executable directly")
        print("4. First run will require QR code scan")
        print("5. Subsequent runs are automatic")
        
        if platform.system() == 'Darwin':  # macOS
            print("\nNote for macOS:")
            print("- First run may require security permission")
            print("- Go to System Preferences > Security & Privacy")
            print("- Click 'Allow' when prompted")
    else:
        print("\n❌ Build failed!")
        print("Check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())