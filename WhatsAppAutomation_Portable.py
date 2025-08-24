#!/usr/bin/env python3
"""
WhatsApp Automation - Portable Version
Cross-platform WhatsApp message automation with configurable settings.
No hardcoded paths - works on any Windows/Mac/Linux system.
"""

import pandas as pd
import json
import os
import sys
import time
import urllib.parse
import logging
import shutil
import platform
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, field

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
    ElementNotInteractableException
)

# Custom imports (made optional for portable deployment)
try:
    from simple_chrome_manager import get_chromedriver_path
except ImportError:
    # Fallback to webdriver-manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        def get_chromedriver_path():
            return ChromeDriverManager().install()
    except ImportError:
        get_chromedriver_path = None

try:
    from logging_manager import setup_logging
except ImportError:
    setup_logging = None


@dataclass
class AppConfig:
    """Comprehensive configuration class loaded from JSON."""
    # Application settings
    app_name: str = "WhatsApp Automation"
    app_version: str = "1.0.0"
    debug_mode: bool = False
    
    # File paths (all relative to app directory)
    csv_path: str = "data/clients.csv"
    active_message_path: str = "templates/active_message.txt"
    inactive_message_path: str = "templates/inactive_message.txt"
    no_instruction_message_path: str = "templates/no_instruction_message.txt"
    log_folder: str = "logs"
    error_log_path: str = "logs/error_log.json"
    summary_csv_path: str = "output/MessageSummary.csv"
    user_data_shs: str = "user_data/profile_shs"
    user_data_sud: str = "user_data/profile_sud"
    
    # Business logic settings
    hearing_date_offset_days: int = 7
    future_date_offset_days: int = 1000
    csv_max_age_hours: int = 48
    csv_warning_age_hours: int = 24
    selected_categories: List[str] = field(default_factory=lambda: ["Active", "NoClientsInstruction"])
    required_csv_columns: List[str] = field(default_factory=lambda: ["Client", "Contact", "NextHearingDate", "Category", "TypRnRy", "Parties"])
    
    # Automation timing settings
    max_session_retries: int = 3
    session_check_timeout: int = 30
    message_send_delay: int = 5
    max_message_retries: int = 2
    webdriver_timeout: int = 20
    login_timeout: int = 60
    cleanup_pause_seconds: int = 30
    
    # UI Selectors
    send_button_selectors: List[str] = field(default_factory=lambda: [
        "//span[@data-testid='send']",
        "//*[@id='main']/footer/div[1]/div/span/div/div[2]/div/div[4]/button",
        "//button[@aria-label='Send']",
        "//div[@data-testid='compose-btn-send']",
        "/html/body/div[1]/div/div/div[3]/div/div[4]/div/footer/div[1]/div/span/div/div[2]/div/div[4]/button",
        "//*[@id='main']/footer/div[1]/div/span/div/div[2]/div/div[4]/button/span"
    ])
    
    chat_loaded_selectors: List[str] = field(default_factory=lambda: [
        "//div[@data-testid='conversation-compose-box-input']",
        "//*[@id='main']/footer/div[1]/div/span/div/div[2]/div/div[1]/div/div[2]",
        "//div[@contenteditable='true'][@data-tab='10']"
    ])
    
    session_selectors: List[Dict] = field(default_factory=lambda: [
        {"type": "ID", "value": "pane-side"},
        {"type": "XPATH", "value": "//div[@data-testid='chat-list']"},
        {"type": "XPATH", "value": "//div[@id='app']//div[contains(@class,'two')]"},
        {"type": "XPATH", "value": "//header[@data-testid='chat-header']"},
        {"type": "XPATH", "value": "//div[@contenteditable='true'][@data-tab='10']"}
    ])
    
    qr_code_selector: str = "//div[@data-testid='qr-code']"
    
    # Chrome options
    chrome_arguments: List[str] = field(default_factory=lambda: [
        "--disable-extensions",
        "--no-sandbox",
        "--disable-dev-shm-usage", 
        "--disable-gpu",
        "--disable-web-security",
        "--allow-running-insecure-content",
        "--disable-features=VizDisplayCompositor",
        "--remote-debugging-port=9222"
    ])
    
    # Notification contacts
    notification_contact1: str = ""
    notification_contact2: str = ""
    
    # Runtime paths (set during initialization)
    app_directory: str = ""
    
    def __post_init__(self):
        """Set up runtime configuration after initialization."""
        if not self.app_directory:
            self.app_directory = self._get_application_directory()
        self._make_paths_absolute()
    
    def _get_application_directory(self):
        """Get the correct application directory for both script and executable modes."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller executable - use directory containing executable
                return os.path.dirname(sys.executable)
            else:
                # Other frozen executables
                return os.path.dirname(sys.executable)
        else:
            # Running as Python script
            return os.path.dirname(os.path.abspath(__file__))
    
    def _make_paths_absolute(self):
        """Convert relative paths to absolute paths based on app directory."""
        path_fields = [
            'csv_path', 'active_message_path', 'inactive_message_path', 
            'no_instruction_message_path', 'log_folder', 'error_log_path',
            'summary_csv_path', 'user_data_shs', 'user_data_sud'
        ]
        
        for field_name in path_fields:
            relative_path = getattr(self, field_name)
            absolute_path = os.path.join(self.app_directory, relative_path)
            setattr(self, field_name, absolute_path)


class PortableWhatsAppAutomation:
    """Portable WhatsApp automation class with configuration-driven behavior."""
    
    def __init__(self, config: AppConfig):
        """Initialize with configuration object."""
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.setup_directories()
        self.setup_logging()
        
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.config.log_folder,
            os.path.dirname(self.config.summary_csv_path),
            self.config.user_data_shs,
            self.config.user_data_sud,
            os.path.dirname(self.config.error_log_path)
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """Initialize portable logging system."""
        if setup_logging:
            # Use custom logging manager if available
            setup_logging(self.config.log_folder, self.config.error_log_path)
        else:
            # Fallback to basic logging
            log_file = os.path.join(
                self.config.log_folder,
                f"automation_{datetime.now().strftime('%Y_%m_%d')}.log"
            )
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler()
                ]
            )
        
        logging.info(f"{self.config.app_name} v{self.config.app_version} initialized")
        logging.info(f"Application directory: {self.config.app_directory}")
    
    @staticmethod
    def load_config(config_path: Optional[str] = None) -> AppConfig:
        """Load configuration from JSON file with fallback to defaults."""
        if not config_path:
            # Try to find config file in same directory as executable/script
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                script_dir = os.path.dirname(sys.executable)
            else:
                # Running as Python script
                script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "app_config.json")
        
        config = AppConfig()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update config with JSON data
                for section, values in config_data.items():
                    if section.startswith('_'):
                        continue  # Skip comments
                        
                    if section == 'paths':
                        for key, value in values.items():
                            if hasattr(config, key):
                                setattr(config, key, value)
                    
                    elif section == 'business_logic':
                        for key, value in values.items():
                            if hasattr(config, key):
                                setattr(config, key, value)
                    
                    elif section == 'automation_settings':
                        for key, value in values.items():
                            if hasattr(config, key):
                                setattr(config, key, value)
                    
                    elif section == 'selectors':
                        for key, value in values.items():
                            if hasattr(config, key):
                                setattr(config, key, value)
                    
                    elif section == 'chrome_options':
                        if 'arguments' in values:
                            config.chrome_arguments = values['arguments']
                    
                    elif section == 'notifications':
                        config.notification_contact1 = values.get('contact1', '')
                        config.notification_contact2 = values.get('contact2', '')
                
                logging.info(f"Configuration loaded from: {config_path}")
                
            except Exception as e:
                logging.warning(f"Failed to load config from {config_path}: {e}")
                logging.info("Using default configuration")
        else:
            logging.info(f"Config file not found at {config_path}, using defaults")
        
        return config
    
    def get_chrome_driver_path(self):
        """Get ChromeDriver path with bulletproof fallback methods."""
        print("🔍 Searching for ChromeDriver...")
        
        # Method 1: Try simple_chrome_manager
        if get_chromedriver_path:
            try:
                print("🔄 Trying simple chrome manager...")
                path = get_chromedriver_path()
                print(f"✅ ChromeDriver found: {path}")
                return path
            except Exception as e:
                print(f"❌ Simple chrome manager failed: {e}")
                logging.warning(f"Simple ChromeDriver manager failed: {e}")
        
        # Method 2: Direct webdriver-manager
        try:
            print("🔄 Trying webdriver-manager...")
            from webdriver_manager.chrome import ChromeDriverManager
            path = ChromeDriverManager().install()
            print(f"✅ webdriver-manager success: {path}")
            return path
        except ImportError:
            print("❌ webdriver-manager not installed")
            print("🔧 Installing webdriver-manager...")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
                from webdriver_manager.chrome import ChromeDriverManager
                path = ChromeDriverManager().install()
                print(f"✅ webdriver-manager installed and working: {path}")
                return path
            except Exception as install_error:
                print(f"❌ Failed to install webdriver-manager: {install_error}")
        except Exception as e:
            print(f"❌ webdriver-manager failed: {e}")
        
        # Method 3: Check for manual ChromeDriver
        print("🔄 Looking for manual ChromeDriver installation...")
        possible_paths = []
        if platform.system().lower() == "windows":
            possible_paths = [
                "chromedriver.exe",
                "C:\\chromedriver.exe",
                os.path.expanduser("~\\chromedriver.exe")
            ]
        else:
            possible_paths = [
                "chromedriver",
                "/usr/local/bin/chromedriver",
                "/usr/bin/chromedriver"
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found manual ChromeDriver: {path}")
                return path
        
        # If all methods fail
        error_msg = """
❌ ChromeDriver not found with any method!

QUICK FIX:
1. Run: python install_chrome_dependencies.py
2. Or run: pip install webdriver-manager
3. Make sure Chrome browser is installed

After running the fix, try again: python start_automation.py shs
"""
        print(error_msg)
        logging.error("ChromeDriver management not available")
        raise RuntimeError("ChromeDriver not found. Run: python install_chrome_dependencies.py")
    
    def _ensure_chrome_directory(self, user_data_dir: str):
        """Ensure Chrome user data directory exists with proper permissions."""
        try:
            # Convert to absolute path
            abs_path = os.path.abspath(user_data_dir)
            
            # Create directory structure
            Path(abs_path).mkdir(parents=True, exist_ok=True)
            
            # Create essential Chrome subdirectories
            essential_dirs = [
                "Default",
                "Default/Local Storage",
                "Default/Session Storage", 
                "Default/IndexedDB",
                "Default/Cache",
                "ShaderCache",
                "SwReporter"
            ]
            
            for subdir in essential_dirs:
                subdir_path = os.path.join(abs_path, subdir)
                Path(subdir_path).mkdir(parents=True, exist_ok=True)
            
            # Windows-specific permissions fix
            if platform.system().lower() == "windows":
                try:
                    import subprocess
                    # Remove any restrictive permissions and grant full control
                    cmd = f'icacls "{abs_path}" /reset /T & icacls "{abs_path}" /grant %username%:F /T'
                    subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    logging.info(f"Windows permissions set for: {abs_path}")
                except Exception as e:
                    logging.warning(f"Could not set Windows permissions for {abs_path}: {e}")
            
            # Set directory permissions on Unix-like systems
            else:
                try:
                    import stat
                    # Set read, write, execute for owner
                    os.chmod(abs_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                except Exception as e:
                    logging.warning(f"Could not set Unix permissions for {abs_path}: {e}")
            
            logging.info(f"Chrome directory prepared: {abs_path}")
            
        except Exception as e:
            logging.error(f"Failed to ensure Chrome directory {user_data_dir}: {e}")
            # Try to create a clean alternative directory
            try:
                clean_dir = f"{user_data_dir}_clean"
                Path(clean_dir).mkdir(parents=True, exist_ok=True)
                logging.info(f"Created clean alternative directory: {clean_dir}")
                return clean_dir
            except Exception as clean_error:
                logging.error(f"Failed to create clean directory: {clean_error}")
                raise e
    
    def backup_user_data(self, user_data_dir: str, backup_dir: str) -> bool:
        """Backup user data directory."""
        try:
            Path(backup_dir).mkdir(parents=True, exist_ok=True)
            
            if not os.path.exists(user_data_dir):
                logging.warning(f"Source directory does not exist: {user_data_dir}")
                return False
            
            for item in os.listdir(user_data_dir):
                src = os.path.join(user_data_dir, item)
                dst = os.path.join(backup_dir, item)
                
                try:
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
                except (FileNotFoundError, PermissionError) as e:
                    logging.warning(f"Skipping {src} during backup: {e}")
                    continue
            
            logging.info(f"User data backed up to: {backup_dir}")
            return True
            
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            return False
    
    @contextmanager
    def webdriver_context(self, user_data_dir: str):
        """Context manager for WebDriver with proper cleanup."""
        driver = None
        try:
            driver = self._initialize_webdriver(user_data_dir)
            yield driver
        except Exception as e:
            logging.error(f"WebDriver context error: {e}")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                    logging.info("WebDriver closed successfully")
                except Exception as e:
                    logging.warning(f"Error closing WebDriver: {e}")
    
    def _initialize_webdriver(self, user_data_dir: str) -> webdriver.Chrome:
        """Initialize Chrome WebDriver with configuration-driven options."""
        try:
            # Ensure directories exist with proper permissions
            self._ensure_chrome_directory(user_data_dir)
            backup_dir = f"{user_data_dir}_Backup"
            
            # Configure Chrome options from config
            options = Options()
            
            # Use absolute path for user data directory (critical for Windows)
            abs_user_data_dir = os.path.abspath(user_data_dir)
            
            # Ensure the directory exists and has proper permissions
            Path(abs_user_data_dir).mkdir(parents=True, exist_ok=True)
            
            # Windows-specific: Fix permissions
            if platform.system().lower() == "windows":
                try:
                    import subprocess
                    # Give full control to current user
                    subprocess.run(f'icacls "{abs_user_data_dir}" /grant %username%:F /T', shell=True, capture_output=True)
                except Exception as perm_error:
                    logging.warning(f"Could not set Windows permissions: {perm_error}")
            
            # Use absolute path in Chrome argument
            options.add_argument(f"--user-data-dir={abs_user_data_dir}")
            
            # Add Chrome stability arguments first
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-features=TranslateUI")
            
            # Additional arguments to help with data directory issues
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions-file-access-check")
            options.add_argument("--disable-extensions-http-throttling")
            options.add_argument("--aggressive-cache-discard")
            
            # Force create the profile directory
            options.add_argument(f"--profile-directory=Default")
            
            # Add configured arguments (but avoid duplicates)
            for arg in self.config.chrome_arguments:
                if arg not in ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]:
                    options.add_argument(arg)
            
            # Add experimental options
            options.add_experimental_option("detach", True)
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            })
            
            # Get ChromeDriver path
            chromedriver_path = self.get_chrome_driver_path()
            service = Service(chromedriver_path)
            
            # Initialize driver
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(self.config.webdriver_timeout)
            
            logging.info("WebDriver initialized successfully")
            
            # Navigate to WhatsApp Web
            driver.get("https://web.whatsapp.com")
            logging.info("Navigated to WhatsApp Web")
            
            # Handle first-time login
            self._handle_initial_login(driver, user_data_dir, backup_dir)
            
            return driver
            
        except Exception as e:
            logging.critical(f"Failed to initialize WebDriver: {e}")
            raise
    
    def _handle_initial_login(self, driver: webdriver.Chrome, user_data_dir: str, backup_dir: str):
        """Handle initial QR code scanning if needed."""
        profile_prefs = os.path.join(user_data_dir, "Default", "Preferences")
        
        if not os.path.exists(profile_prefs):
            logging.info(
                "No previous session found. Please scan the QR code to log in.\n"
                "Press Enter after scanning to continue..."
            )
            input()
            
            # Wait for successful login
            try:
                WebDriverWait(driver, self.config.login_timeout).until(
                    EC.presence_of_element_located((By.ID, "pane-side"))
                )
                logging.info("Login successful")
                
                # Create backup after successful login
                if not os.path.exists(backup_dir):
                    self.backup_user_data(user_data_dir, backup_dir)
                    
            except TimeoutException:
                raise Exception("Login timeout - QR code not scanned in time")
        else:
            logging.info("Existing session found - should be logged in automatically")
    
    def check_session(self, driver: webdriver.Chrome) -> bool:
        """Check WhatsApp Web session using configured selectors."""
        for attempt in range(1, self.config.max_session_retries + 1):
            try:
                logging.info(f"Checking session (attempt {attempt}/{self.config.max_session_retries})")
                
                # Try configured session selectors
                for selector_config in self.config.session_selectors:
                    try:
                        selector_type = selector_config["type"]
                        selector_value = selector_config["value"]
                        
                        if selector_type == "ID":
                            by_type = By.ID
                        else:
                            by_type = By.XPATH
                        
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((by_type, selector_value))
                        )
                        logging.info(f"Session active - detected element: {selector_value}")
                        return True
                    except TimeoutException:
                        continue
                
                # Check for QR code (means need login)
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, self.config.qr_code_selector))
                    )
                    logging.warning("QR code detected - session requires login")
                    return False
                except TimeoutException:
                    pass
                
                logging.warning(f"Session check attempt {attempt} - no clear indicators found")
                if attempt < self.config.max_session_retries:
                    time.sleep(10)
                    
            except Exception as e:
                logging.warning(f"Session check attempt {attempt} error: {e}")
                if attempt < self.config.max_session_retries:
                    time.sleep(10)
        
        logging.error("WhatsApp Web session status unclear after all retries")
        return False
    
    def send_whatsapp_message(self, driver: webdriver.Chrome, name: str, contact: str, message: str) -> bool:
        """Send WhatsApp message using configured selectors."""
        for attempt in range(1, self.config.max_message_retries + 1):
            try:
                logging.info(f"Sending message to {name} ({contact}) - attempt {attempt}")
                
                # Construct URL and navigate
                encoded_message = urllib.parse.quote(message)
                url = f"https://web.whatsapp.com/send?phone={contact}&text={encoded_message}"
                driver.get(url)
                
                # Wait for chat to load using configured selectors
                chat_loaded = False
                for selector in self.config.chat_loaded_selectors:
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        chat_loaded = True
                        break
                    except TimeoutException:
                        continue
                
                if not chat_loaded:
                    raise TimeoutException("Chat interface failed to load")
                
                # Find and click send button using configured selectors
                send_button = None
                for selector in self.config.send_button_selectors:
                    try:
                        send_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        logging.info(f"Send button found with selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not send_button:
                    raise NoSuchElementException("Send button not found with any configured selector")
                
                # Click send button with retry
                try:
                    time.sleep(2)  # Brief pause before clicking
                    send_button.click()
                    time.sleep(3)  # Wait for message to send
                    
                    logging.info(f"Message sent successfully to {name} ({contact})")
                    return True
                    
                except ElementNotInteractableException:
                    # Try JavaScript click as fallback
                    driver.execute_script("arguments[0].click();", send_button)
                    time.sleep(3)
                    logging.info(f"Message sent via JavaScript to {name} ({contact})")
                    return True
                
            except Exception as e:
                logging.warning(f"Message send attempt {attempt} failed for {name}: {e}")
                if attempt < self.config.max_message_retries:
                    time.sleep(5)  # Wait before retry
                else:
                    logging.error(f"Failed to send message to {name} after all retries: {e}")
        
        return False
    
    def load_csv_data(self) -> pd.DataFrame:
        """Load and validate CSV data using configured parameters."""
        try:
            # Debug logging for path resolution
            logging.info(f"CSV path (before resolution): {self.config.csv_path}")
            logging.info(f"Application directory: {self.config.app_directory}")
            logging.info(f"Current working directory: {os.getcwd()}")
            
            # Ensure we have absolute paths
            if not os.path.isabs(self.config.csv_path):
                self.config.csv_path = os.path.join(self.config.app_directory, self.config.csv_path)
                logging.info(f"CSV path (after resolution): {self.config.csv_path}")
            
            # Check if data directory exists
            data_dir = os.path.dirname(self.config.csv_path)
            logging.info(f"Data directory: {data_dir}")
            logging.info(f"Data directory exists: {os.path.exists(data_dir)}")
            if os.path.exists(data_dir):
                logging.info(f"Contents of data directory: {os.listdir(data_dir)}")
            
            # Check file existence and age
            if not os.path.exists(self.config.csv_path):
                # Try to find any CSV files in the data directory
                if os.path.exists(data_dir):
                    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                    if csv_files:
                        logging.info(f"Found CSV files in data directory: {csv_files}")
                        # Use the first CSV file found
                        found_csv = os.path.join(data_dir, csv_files[0])
                        logging.info(f"Using CSV file: {found_csv}")
                        self.config.csv_path = found_csv
                    else:
                        raise FileNotFoundError(f"No CSV files found in data directory: {data_dir}")
                else:
                    raise FileNotFoundError(f"CSV file not found: {self.config.csv_path}")
            
            csv_modified_time = datetime.fromtimestamp(os.path.getmtime(self.config.csv_path))
            age_hours = (datetime.now() - csv_modified_time).total_seconds() / 3600
            
            if age_hours > self.config.csv_max_age_hours:
                raise ValueError(f"CSV file is too old ({age_hours:.1f} hours). Please update it.")
            elif age_hours > self.config.csv_warning_age_hours:
                logging.warning(f"CSV file is {age_hours:.1f} hours old - consider updating")
            
            # Load and process data
            df = pd.read_csv(self.config.csv_path, dtype={"Contact": str})
            df['Contact'] = df['Contact'].str.replace(" ", "").str.strip()
            
            # Validate required columns from config
            missing_columns = [col for col in self.config.required_csv_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            logging.info(f"CSV loaded successfully: {len(df)} records from {csv_modified_time}")
            
            # Export to additional formats
            self._export_data_formats(df)
            
            return df
            
        except Exception as e:
            logging.error(f"Failed to load CSV data: {e}")
            raise
    
    def _export_data_formats(self, df: pd.DataFrame):
        """Export data to Excel and JSON formats."""
        try:
            base_path = os.path.splitext(self.config.csv_path)[0]
            
            # Export to Excel
            excel_path = f"{base_path}.xlsx"
            df.to_excel(excel_path, index=False)
            logging.info(f"Data exported to Excel: {excel_path}")
            
            # Export to JSON
            json_path = f"{base_path}.json"
            df.to_json(json_path, orient="records", force_ascii=False, indent=4)
            logging.info(f"Data exported to JSON: {json_path}")
            
        except Exception as e:
            logging.warning(f"Failed to export data formats: {e}")
    
    def load_message_templates(self) -> Dict[str, str]:
        """Load message templates from configured paths."""
        templates = {}
        template_paths = {
            'Active': self.config.active_message_path,
            'Inactive': self.config.inactive_message_path,
            'NoClientsInstruction': self.config.no_instruction_message_path
        }
        
        for category, path in template_paths.items():
            try:
                # Ensure we have absolute paths for templates
                if not os.path.isabs(path):
                    path = os.path.join(self.config.app_directory, path)
                
                with open(path, 'r', encoding='utf-8') as f:
                    template = f.read().strip()
                    if not template:
                        raise ValueError(f"Template file is empty: {path}")
                    templates[category] = template
                    logging.info(f"Loaded template for {category}")
            except Exception as e:
                logging.error(f"Failed to load template for {category}: {e}")
                raise
        
        return templates
    
    def filter_and_prepare_messages(self, df: pd.DataFrame, templates: Dict[str, str]) -> List[Tuple]:
        """Filter clients and prepare messages using configured business logic."""
        try:
            # Convert date column
            df = df.copy()
            df['NextHearingDate'] = pd.to_datetime(df['NextHearingDate'], errors='coerce').dt.date
            
            # Calculate target dates using configured offsets
            today = datetime.now().date() + timedelta(days=self.config.hearing_date_offset_days)
            future_date = today + timedelta(days=self.config.future_date_offset_days)
            
            # Filter using configured categories
            filtered_df = df[df['Category'].isin(self.config.selected_categories)].copy()
            
            # Filter by dates
            target_clients = filtered_df[
                filtered_df['NextHearingDate'].isin([today, future_date])
            ].copy()
            
            logging.info(f"Filtered {len(target_clients)} clients for messaging")
            
            # Prepare messages
            messages = []
            for _, row in target_clients.iterrows():
                try:
                    category = row['Category']
                    if category not in templates:
                        logging.warning(f"No template for category: {category}")
                        continue
                    
                    # Replace placeholders in message template
                    message = templates[category]
                    for col in df.columns:
                        if col in row and pd.notna(row[col]):
                            placeholder = f"{{{col}}}"
                            message = message.replace(placeholder, str(row[col]))
                    
                    messages.append((
                        row['Client'],
                        row['Contact'],
                        row['NextHearingDate'],
                        message
                    ))
                    
                except Exception as e:
                    logging.warning(f"Failed to prepare message for {row.get('Client', 'Unknown')}: {e}")
                    continue
            
            logging.info(f"Prepared {len(messages)} messages")
            return messages
            
        except Exception as e:
            logging.error(f"Failed to filter and prepare messages: {e}")
            raise
    
    def send_notification_summary(self, driver: webdriver.Chrome, summary: List[Dict], total_messages: int, successful_messages: int):
        """Send notification summary to configured admin contacts."""
        try:
            # Create summary DataFrame
            summary_df = pd.DataFrame(summary)
            summary_text = summary_df[['Client', 'Message Status']].to_string(index=False, header=True)
            
            # Format notification message
            hearing_date = datetime.now().date() + timedelta(days=self.config.hearing_date_offset_days)
            notification_message = (
                f"WhatsApp Automation Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"Successfully delivered messages for hearing date {hearing_date} to "
                f"{successful_messages} out of {total_messages} clients.\n\n"
                f"Detailed Summary:\n{summary_text}"
            )
            
            # Send to configured notification contacts
            contacts = [self.config.notification_contact1, self.config.notification_contact2]
            for contact in contacts:
                if contact:
                    logging.info(f"Sending notification to {contact}")
                    success = self.send_whatsapp_message(driver, "Admin", contact, notification_message)
                    if success:
                        logging.info(f"Notification sent successfully to {contact}")
                    else:
                        logging.error(f"Failed to send notification to {contact}")
                    time.sleep(5)
            
        except Exception as e:
            logging.error(f"Failed to send notification summary: {e}")
    
    def save_summary(self, summary: List[Dict]):
        """Save message summary to configured CSV path."""
        try:
            summary_df = pd.DataFrame(summary)
            summary_df.to_csv(self.config.summary_csv_path, index=False)
            logging.info(f"Summary saved to: {self.config.summary_csv_path}")
        except Exception as e:
            logging.error(f"Failed to save summary: {e}")
    
    def run(self, user_data_type: str = "shs"):
        """Main execution method with configuration-driven behavior."""
        try:
            logging.info("Starting portable WhatsApp automation process")
            
            # Determine user data directory from config
            user_data_dir = (
                self.config.user_data_shs if user_data_type.lower() == "shs"
                else self.config.user_data_sud
            )
            
            # Load data and templates
            df = self.load_csv_data()
            templates = self.load_message_templates()
            messages = self.filter_and_prepare_messages(df, templates)
            
            if not messages:
                logging.warning("No messages to send")
                return
            
            # Process messages with WebDriver
            with self.webdriver_context(user_data_dir) as driver:
                if not self.check_session(driver):
                    raise Exception("WhatsApp Web session is inactive")
                
                # Send messages
                summary = []
                successful_count = 0
                
                for index, (name, contact, hearing_date, message) in enumerate(messages, 1):
                    logging.info(f"Processing message {index}/{len(messages)} for {name}")
                    
                    success = self.send_whatsapp_message(driver, name, contact, message)
                    status = "Success" if success else "Failed"
                    
                    if success:
                        successful_count += 1
                    
                    summary.append({
                        "Client": name,
                        "Phone Number": contact,
                        "Next Hearing Date": hearing_date,
                        "Message Status": status
                    })
                    
                    logging.info(f"[MESSAGE STATUS] Message {index} to {contact}: {status}")
                    
                    # Configurable delay between messages
                    if index < len(messages):
                        time.sleep(self.config.message_send_delay)
                
                # Send notifications and save summary
                self.send_notification_summary(driver, summary, len(messages), successful_count)
                self.save_summary(summary)
                
                # Configurable final pause before cleanup
                logging.info("Pausing before cleanup...")
                time.sleep(self.config.cleanup_pause_seconds)
            
            logging.info(f"Automation completed: {successful_count}/{len(messages)} messages sent successfully")
            
        except Exception as e:
            logging.error(f"Automation failed: {e}")
            raise


def main():
    """Main entry point with portable configuration loading."""
    try:
        # Load configuration (looks for app_config.json in same directory)
        config = PortableWhatsAppAutomation.load_config()
        
        # Initialize automation
        automation = PortableWhatsAppAutomation(config)
        
        # Determine user data type from command line arguments
        user_data_type = "shs"  # default
        if len(sys.argv) >= 2:
            provided_type = sys.argv[1].lower()
            if provided_type in ["shs", "sud"]:
                user_data_type = provided_type
            else:
                logging.warning(f"Invalid user data type: {provided_type}. Using default: shs")
        
        # Run automation
        automation.run(user_data_type)
        
    except Exception as e:
        logging.critical(f"Critical error in main execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()