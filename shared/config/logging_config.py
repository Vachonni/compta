"""Centralized logging configuration for all services."""

import logging
import logging.config
import os

from typing import Optional

def setup_logging(service_name: Optional[str] = None) -> None:
    """
    Set up logging configuration. Optionally, pass a service_name to tag logs.
    Log level and output can be controlled via environment variables:
      LOG_LEVEL, LOG_FILE
    """
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str | None = os.getenv("LOG_FILE")
    # Format: timestamp level [service] logger: message (no milliseconds)
    if service_name:
        fmt = f"%(asctime)s %(levelname)s [{service_name}] %(name)s: %(message)s"
    else:
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"

    # Remove milliseconds from asctime by setting datefmt
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers = ["console"]
    handler_dict = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": log_level,
        }
    }
    if log_file:
        handlers.append("file")
        handler_dict["file"] = {
            "class": "logging.FileHandler",
            "formatter": "default",
            "level": log_level,
            "filename": log_file,
        }

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": fmt,
                "datefmt": datefmt,
            },
        },
        "handlers": handler_dict,
        "root": {
            "handlers": handlers,
            "level": log_level,
        },
    }
    logging.config.dictConfig(logging_config)
