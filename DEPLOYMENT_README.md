# WhatsApp Automation - Deployment Package

## Quick Start

### Option 1: Python Script (Recommended)
1. Ensure Python 3.7+ is installed
2. Install dependencies: `pip install pandas selenium webdriver-manager openpyxl`
3. Run: `python start_automation.py shs`

### Option 2: Platform-specific
- **Windows**: Run `run_automation.bat`
- **Mac/Linux**: Run `./run_automation.sh`

### Option 3: Direct execution
- Run: `python WhatsAppAutomation_Portable.py shs`

## Configuration
1. Edit `app_config.json` for your settings
2. Replace `data/clients.csv` with your client data
3. Customize message templates in `templates/` folder

## First Run
- The app will open Chrome and show QR code
- Scan with your WhatsApp mobile app
- Login will be remembered for future runs

## Files Created
- `logs/` - Application logs
- `output/` - Message summaries
- `user_data/` - WhatsApp login sessions

Generated on: 2025-08-21 22:12:28
