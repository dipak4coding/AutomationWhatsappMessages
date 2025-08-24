#!/usr/bin/env python3
"""
Universal startup script for WhatsApp Automation
Creates necessary directories and files, then runs the automation
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

def create_message_templates(script_dir):
    """Create message template files if they don't exist."""
    templates_dir = os.path.join(script_dir, 'templates')
    
    templates = {
        'active_message.txt': """Dear {Client},

Your hearing for case {TypRnRy} vs {Parties} is scheduled for {NextHearingDate}.

Please be present at the court.

Best regards,
Sarathi Legal Firm""",
        
        'inactive_message.txt': """Dear {Client},

This is a reminder about your case {TypRnRy} vs {Parties}.

Please contact us for status update.

Best regards,
Sarathi Legal Firm""",
        
        'no_instruction_message.txt': """Dear {Client},

This is a reminder about your upcoming hearing on {NextHearingDate}.

Please contact us for further instructions.

Best regards,
Sarathi Legal Firm"""
    }
    
    for template_name, template_content in templates.items():
        template_path = os.path.join(templates_dir, template_name)
        if not os.path.exists(template_path):
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            print(f"Created template: {template_name}")

def create_config_file(script_dir):
    """Create app_config.json if it doesn't exist."""
    config_path = os.path.join(script_dir, 'app_config.json')
    
    if not os.path.exists(config_path):
        config_content = """{
  "_comment": "WhatsApp Automation - Portable Configuration File",
  "_version": "1.0",
  "_created": "2025-08-23",
  "application": {
    "name": "WhatsApp Automation",
    "version": "1.0.0",
    "debug_mode": false
  },
  "paths": {
    "_comment": "All paths are relative to the application directory",
    "csv_path": "data/clients.csv",
    "active_message_path": "templates/active_message.txt",
    "inactive_message_path": "templates/inactive_message.txt",
    "no_instruction_message_path": "templates/no_instruction_message.txt",
    "log_folder": "logs",
    "error_log_path": "logs/error_log.json",
    "summary_csv_path": "output/MessageSummary.csv",
    "user_data_shs": "user_data/profile_shs",
    "user_data_sud": "user_data/profile_sud"
  },
  "business_logic": {
    "_comment": "Core business rules and calculations",
    "hearing_date_offset_days": 7,
    "future_date_offset_days": 1000,
    "csv_max_age_hours": 48,
    "csv_warning_age_hours": 24,
    "selected_categories": [
      "Active",
      "NoClientsInstruction"
    ],
    "required_csv_columns": [
      "Client",
      "Contact",
      "NextHearingDate",
      "Category",
      "TypRnRy",
      "Parties"
    ]
  },
  "automation_settings": {
    "_comment": "Timing and retry configurations",
    "max_session_retries": 3,
    "session_check_timeout": 30,
    "message_send_delay": 5,
    "max_message_retries": 2,
    "webdriver_timeout": 20,
    "login_timeout": 60,
    "cleanup_pause_seconds": 30
  },
  "selectors": {
    "_comment": "XPath and CSS selectors for WhatsApp Web elements",
    "send_button_selectors": [
      "//span[@data-testid='send']",
      "//*[@id='main']/footer/div[1]/div/span/div/div[2]/div/div[4]/button",
      "//button[@aria-label='Send']",
      "//div[@data-testid='compose-btn-send']",
      "/html/body/div[1]/div/div/div[3]/div/div[4]/div/footer/div[1]/div/span/div/div[2]/div/div[4]/button",
      "//*[@id='main']/footer/div[1]/div/span/div/div[2]/div/div[4]/button/span"
    ],
    "chat_loaded_selectors": [
      "//div[@data-testid='conversation-compose-box-input']",
      "//*[@id='main']/footer/div[1]/div/span/div/div[2]/div/div[1]/div/div[2]",
      "//div[@contenteditable='true'][@data-tab='10']"
    ],
    "session_selectors": [
      {
        "type": "ID",
        "value": "pane-side",
        "description": "Main chat pane"
      },
      {
        "type": "XPATH",
        "value": "//div[@data-testid='chat-list']",
        "description": "Chat list"
      },
      {
        "type": "XPATH",
        "value": "//div[@id='app']//div[contains(@class,'two')]",
        "description": "Two-pane layout"
      },
      {
        "type": "XPATH",
        "value": "//header[@data-testid='chat-header']",
        "description": "Any chat header"
      },
      {
        "type": "XPATH",
        "value": "//div[@contenteditable='true'][@data-tab='10']",
        "description": "Message input"
      }
    ],
    "qr_code_selector": "//div[@data-testid='qr-code']"
  },
  "chrome_options": {
    "_comment": "Chrome browser configuration options",
    "arguments": [
      "--disable-extensions",
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--disable-web-security",
      "--allow-running-insecure-content",
      "--disable-features=VizDisplayCompositor",
      "--remote-debugging-port=9222"
    ]
  },
  "notifications": {
    "_comment": "Admin notification contacts",
    "contact1": "+917756991516",
    "contact2": "+491736620608"
  }
}"""
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("Created configuration file: app_config.json")

def setup_and_run():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("WhatsApp Automation - Universal Startup")
    print("=" * 40)
    print(f"Running from: {script_dir}")
    
    # Create necessary directories
    directories = ['data', 'templates', 'logs', 'output', 'user_data', 'user_data/profile_shs', 'user_data/profile_sud']
    for directory in directories:
        dir_path = os.path.join(script_dir, directory)
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory: {directory}")
    
    # Create configuration file
    create_config_file(script_dir)
    
    # Create message templates
    create_message_templates(script_dir)
    
    # Create sample CSV if it doesn't exist
    csv_path = os.path.join(script_dir, 'data', 'clients.csv')
    if not os.path.exists(csv_path):
        target_date = datetime.now().date() + timedelta(days=7)
        csv_content = f"""Client,Contact,NextHearingDate,Category,TypRnRy,Parties
Test Client,+1234567890,{target_date},Active,Test Case,Test vs Test
Test Client 2,+0987654321,{target_date},NoClientsInstruction,Test Case 2,Test2 vs Test2"""
        
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        print("✓ Created sample CSV file")
    else:
        print("✓ CSV file exists")
    
    # Change to script directory to ensure relative paths work
    os.chdir(script_dir)
    print(f"✓ Changed to directory: {script_dir}")
    
    # Get user data type from command line arguments
    user_data_type = "shs"  # default
    if len(sys.argv) >= 2:
        provided_type = sys.argv[1].lower()
        if provided_type in ["shs", "sud"]:
            user_data_type = provided_type
        else:
            print(f"⚠️ Invalid user data type: {provided_type}. Using default: shs")
    
    print(f"✓ Using profile: {user_data_type}")
    print("=" * 40)
    print("Starting WhatsApp Automation...")
    print("=" * 40)
    
    # Import and run the main automation
    try:
        from WhatsAppAutomation_Portable import main
        # Override sys.argv to pass the user_data_type
        original_argv = sys.argv[:]
        sys.argv = [sys.argv[0], user_data_type]
        main()
        sys.argv = original_argv
    except ImportError as e:
        print(f"❌ Error: WhatsAppAutomation_Portable.py not found! {e}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running automation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    setup_and_run()
