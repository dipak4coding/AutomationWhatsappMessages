# WhatsApp Automation Troubleshooting Guide

## Chrome Data Directory Error: "google chrome cannot read and write to its data directory"

### Quick Fix (Windows):
```bash
python fix_chrome_data_directory.py
```

### Manual Fix Steps:

#### Windows:
1. Close all Chrome/ChromeDriver processes:
   ```cmd
   taskkill /f /im chrome.exe /t
   taskkill /f /im chromedriver.exe /t
   ```

2. Delete the problematic directory:
   ```cmd
   rmdir /s "user_data\profile_shs"
   ```

3. Run the automation again - it will create a fresh directory:
   ```cmd
   python start_automation.py shs
   ```

#### Mac/Linux:
1. Close Chrome processes:
   ```bash
   pkill -f chrome
   pkill -f chromedriver
   ```

2. Remove the directory:
   ```bash
   rm -rf user_data/profile_shs
   ```

3. Run the automation:
   ```bash
   python start_automation.py shs
   ```

## Common Solutions

### 1. ChromeDriver Issues
```bash
python install_chrome_dependencies.py
```

### 2. Python/PyInstaller Issues
```bash
python fix_pyinstaller.py
```

### 3. Missing Files
```bash
python start_automation.py shs
```
This creates all missing files automatically.

## Error Patterns & Solutions

| Error | Solution |
|-------|----------|
| `ChromeDriver not found` | `python install_chrome_dependencies.py` |
| `CSV file not found` | Run from the correct directory or use `python start_automation.py` |
| `Template files missing` | `python start_automation.py` creates them |
| `Chrome cannot read data directory` | `python fix_chrome_data_directory.py` |
| `PyInstaller bootloader` | `python fix_pyinstaller.py` or use Python directly |
| `Session requires login` | Delete `user_data` folder and scan QR again |

## Test Your Installation

### Test ChromeDriver:
```bash
python -c "from simple_chrome_manager import get_chromedriver_path; print(get_chromedriver_path())"
```

### Test Chrome Directory:
```bash
python fix_chrome_data_directory.py
```

### Test Full Automation:
```bash
python start_automation.py shs
```

## Environment Requirements

- **Windows**: Python 3.8-3.12 (avoid 3.13)
- **Chrome Browser**: Latest version
- **Required Packages**: Run `pip install -r requirements.txt` if available

## Support

If issues persist:
1. Check the log files in the `logs/` directory
2. Run with `python start_automation.py shs` for detailed output
3. Ensure Chrome browser is properly installed
4. Try running as administrator (Windows) if permission issues persist

## Alternative: Use Python Directly

Instead of executables, always works:
```bash
python start_automation.py shs
```

This approach:
- ✅ Works on all systems
- ✅ Creates missing files automatically
- ✅ Provides better error messages
- ✅ No PyInstaller dependencies