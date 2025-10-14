import os
import sys
from typing import Optional
from loguru import logger


def setup_logger(
    level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format=format,
        level=level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        logger.add(
            log_file,
            format=format,
            level=level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
        )


def get_logger(name: str | None = None):
    return logger.bind(name=name) if name else logger


def init_logger() -> None:
    level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        fmt = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    else:
        fmt = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    setup_logger(level=level, log_file=log_file, format=fmt)


# Initialize on import by default
init_logger()

__all__ = ["logger", "get_logger", "setup_logger", "init_logger"]

