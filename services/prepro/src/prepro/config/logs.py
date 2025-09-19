"""Configuration of logger for project prepro"""

import logging
import logging.config

from prepro.config.settings import settings


PROJECT_NAME = "prepro"


def setup_logging() -> None:
    """
    Set up logging configuration.
    """
    # Format: timestamp level [service] logger: message (no milliseconds)
    fmt = f"%(asctime)s %(levelname)s [{PROJECT_NAME}] %(name)s: %(message)s"
    # Remove milliseconds from asctime by setting datefmt
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers = ["console"]
    handler_dict = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": settings.log_level,
        }
    }

    logging_config: dict[str, object] = {
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
            "level": settings.log_level,
        },
    }
    logging.config.dictConfig(logging_config)
