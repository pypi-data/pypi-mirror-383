import enum
import os
import logging
from datetime import datetime

class LogConfig:
    
    """
    Configuration constants for the application.
    """
    def __init__(self):
        pass
            
    CREATED_TIME = f"{datetime.date}-{datetime.time}"
    
#Logging Levels
    LOG_LEVELS: enum = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    
    LOG_FILE = f"{__name__}-{CREATED_TIME}.log"
    # Logging configuration
    if not os.path.exists(".env"):
        LOG_LEVEL = logging.os.getenv("LOG_LEVEL", LOG_LEVELS.get("INFO"))
    else:
        LOG_LEVEL= LOG_LEVELS.get("INFO")
    # Log file directory and file
    if os.path.exists(".logs"):
        LOG_DIR = "./logs"
    else:
        os.makedirs("./logs", exist_ok=True)

    DOTENV_PATH = ".env"
    
LogConfig()    
