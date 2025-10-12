import os
import sys
import logging
from .config import LogConfig
from datetime import datetime

class ColorFormatter(logging.Formatter):
    # ANSI escape codes for coloured output
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'RESET': '\033[0m'
    }

    def format(self, record):
        colour = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        message = super().format(record)
        return f"{colour}{message}{reset}"

def get_logger(name: str = "dental_logger", log_level=LogConfig.LOG_LEVEL):
    # Ensure log directory exists
    log_dir = LogConfig.LOG_FILE
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{__name__}-{LogConfig.LOG_FILE}-{datetime.now()}.log")

    logger = logging.getLogger(__name__)
    logger.setLevel(LogConfig.LOG_LEVEL)
    logger.propagate = False  # Prevent double logging

    if not logger.handlers:
        # Console handler with colour
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch_formatter = ColorFormatter('[%(asctime)s] %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)

        # File handler (no color, as files should be plain)
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(log_level)
        fh_formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)

    return logger




