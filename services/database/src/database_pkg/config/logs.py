import logging
import logging.config

from database_pkg.config.settings import database_settings


def setup_logging() -> None:
    """
    Set up logging configuration.
    Log level and output can be controlled via environment variables
    LOG_LEVEL and LOG_FILE.
    """
    fmt = f"%(asctime)s %(levelname)s [{database_settings.SERVICE_NAME}] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers = ["console"]
    handler_dict = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": database_settings.log_level,
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
            "level": database_settings.log_level,
        },
    }
    logging.config.dictConfig(logging_config)
