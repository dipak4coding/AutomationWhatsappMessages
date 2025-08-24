# WhatsApp Automation - How to Use

## 🚀 Quick Start (3 Options)

### Option 1: Python Script (Easiest)
```bash
python start_automation.py shs
```

### Option 2: Create Standalone Executable
```bash
python create_executable.py
# This creates WhatsAppAutomation.exe (Windows) or WhatsAppAutomation (Mac)
# Then run: ./WhatsAppAutomation shs
```

### Option 3: Direct Script
```bash
python WhatsAppAutomation_Portable.py shs
```

## 📋 Requirements

- **Google Chrome browser** (must be installed)
- **Python 3.7+** (for script mode)
- **Internet connection** (for ChromeDriver download)

For executable mode: No Python needed!

## ⚙️ Configuration

### 1. Update Client Data
Replace `data/clients.csv` with your client data:
```csv
Client,Contact,NextHearingDate,Category,TypRnRy,Parties
John Smith,+1234567890,2025-08-30,Active,Civil Case,John vs ABC
```

### 2. Configure Settings
Edit `app_config.json`:
```json
{
  "business_logic": {
    "hearing_date_offset_days": 7,     // Send messages X days before hearing
    "selected_categories": ["Active", "NoClientsInstruction"]
  },
  "notifications": {
    "contact1": "+917756991516",       // Your admin contact 1
    "contact2": "+491736620608"        // Your admin contact 2
  }
}
```

### 3. Customize Messages
Edit files in `templates/` folder:
- `active_message.txt` - For active clients
- `inactive_message.txt` - For inactive clients  
- `no_instruction_message.txt` - For no-instruction clients

Use placeholders like `{Client}`, `{NextHearingDate}`, `{TypRnRy}`, `{Parties}`

## 🔐 First Time Setup

1. Run the automation: `python start_automation.py shs`
2. Chrome will open to WhatsApp Web
3. **Scan QR code** with your WhatsApp mobile app
4. Login will be saved - **no need to scan again!**

## 📱 User Profiles

- `shs` profile: `python start_automation.py shs`
- `sud` profile: `python start_automation.py sud`

Each profile maintains separate WhatsApp logins.

## 📊 Output Files

- `logs/` - Application logs
- `output/MessageSummary.csv` - Message delivery report
- `user_data/` - WhatsApp login sessions (don't delete!)

## 🔧 Troubleshooting

### "CSV file not found"
- Make sure `data/clients.csv` exists
- Check file has correct columns

### "Chrome/ChromeDriver issues"
- Ensure Google Chrome is installed
- App will auto-download correct ChromeDriver

### "Session requires login"
- Delete `user_data/` folder
- Restart app and scan QR code again

### "Send button not found"
- WhatsApp UI changed
- Update `send_button_selectors` in `app_config.json`

### "No messages to send"
- Check hearing dates in CSV match your offset days
- Verify `selected_categories` in config

## 🎯 Customization Examples

### Change Hearing Date Logic
```json
{"business_logic": {"hearing_date_offset_days": 10}}
```

### Add New Category
```json
{"business_logic": {"selected_categories": ["Active", "Urgent", "NoClientsInstruction"]}}
```

### Slower Message Sending
```json
{"automation_settings": {"message_send_delay": 10}}
```

## 📦 Distribution

To share with others:
1. Copy entire `WhatsAppAutomation_Deploy/` folder
2. Update `app_config.json` for their settings
3. Replace `data/clients.csv` with their data
4. They run: `python start_automation.py shs`

## 🔒 Security Notes

- All data stays on your computer
- No external servers involved
- WhatsApp login saved locally
- Delete `user_data/` to clear sessions

## 📞 Support

Check logs in `logs/` folder for detailed error information.

**That's it! Your WhatsApp automation is ready to use!** 🎉