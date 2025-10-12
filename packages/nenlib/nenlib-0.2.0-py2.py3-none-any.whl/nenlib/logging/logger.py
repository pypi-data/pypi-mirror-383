import logging
from datetime import datetime
import os

def setup_logger():
    logger = logging.getLogger("nenlib")
    logger.setLevel(logging.INFO)
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/nenlib-{datetime.now().strftime('%Y-%m-%d')}.log"
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger