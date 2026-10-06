import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Ensure output directory exists for the log file
OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

LOG_FILE = OUTPUT_DIR / "netscope.log"

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger that writes to both console and a file.
    """
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, return it to prevent duplicate logs
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File Handler
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=2
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
