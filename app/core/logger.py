import logging
import sys
from pathlib import Path
from loguru import logger

# Constants
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Common config for file sinks
FILE_CONFIG = {
    "rotation": "500 MB",
    "retention": "10 days",
    "compression": "zip",
    "enqueue": True,
    "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {extra} | {message}"
}

def filter_error(record):
    """Capture ERROR and CRITICAL logs."""
    return record["level"].no >= logger.level("ERROR").no

def filter_application(record):
    """
    Capture INFO+ logs that are NOT special types (access, security, audit).
    This handles the general business logic logs.
    Also excludes noisy reloader logs.
    """
    name = record["extra"].get("name")
    is_special = name in ["access", "security", "audit"]
    
    # Exclude reloader logs (watchfiles, uvicorn.reloader)
    is_noisy = record["name"].startswith("watchfiles") or record["name"].startswith("uvicorn.reloader")
    
    return record["level"].no >= logger.level("INFO").no and not is_special and not is_noisy

def make_filter(name_value):
    """Create a filter for a specific 'name' binding."""
    def filter_func(record):
        return record["extra"].get("name") == name_value
    return filter_func

class InterceptHandler(logging.Handler):
    """
    Intercept standard Python logging and redirect to Loguru.
    """
    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    # 1. Intercept Standard Logging (Uvicorn, FastAPI, etc.)
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)

    # Hijack all existing loggers to ensure they go through our interceptor
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # 2. Reset Loguru configuration
    logger.remove()

    # 3. Add Console Sink (Stderr)
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # 4. Add File Sinks
    
    # Error Log
    logger.add(
        LOGS_DIR / "error.log",
        level="ERROR",
        filter=filter_error,
        backtrace=True,
        diagnose=True,
        **FILE_CONFIG
    )

    # Application Log
    logger.add(
        LOGS_DIR / "application.log",
        level="INFO",
        filter=filter_application,
        **FILE_CONFIG
    )

    # Specialized Logs (Access, Security, Audit)
    for log_name in ["access", "security", "audit"]:
        logger.add(
            LOGS_DIR / f"{log_name}.log",
            level="INFO",
            filter=make_filter(log_name),
            **FILE_CONFIG
        )

    logger.info("Logging configuration initialized.")
