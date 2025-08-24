import logging
from logging.handlers import RotatingFileHandler
import os
import json
from datetime import datetime


class JsonErrorHandler(logging.Handler):
    def __init__(self, error_log_path):
        super().__init__()
        self.error_log_path = error_log_path

    def emit(self, record):
        if record.levelno >= logging.WARNING:
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": record.levelname,
                "message": record.getMessage()
            }
            if os.path.exists(self.error_log_path):
                with open(self.error_log_path, "r+") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
                    data.append(error_entry)
                    f.seek(0)
                    json.dump(data, f, indent=2)
            else:
                with open(self.error_log_path, "w") as f:
                    json.dump([error_entry], f, indent=2)


def setup_logging(LOG_FOLDER, ERROR_LOG_PATH):

    os.makedirs(LOG_FOLDER, exist_ok=True)
    current_date = datetime.now().strftime("%Y_%m_%d")
    log_file_path = os.path.join(
        LOG_FOLDER, f"AutomationLog_{current_date}.log")

    # Remove all handlers to avoid duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"))

    json_error_handler = JsonErrorHandler(ERROR_LOG_PATH)
    json_error_handler.setLevel(logging.WARNING)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler, json_error_handler]
    )

    logging.info("\n" + "-" * 80)
    logging.info("New Script Run Started")
    logging.info("-" * 80)
    logging.info(
        f"Logging initialized. Logs will be saved to: {log_file_path}")
