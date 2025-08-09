import logging
import sqlite3

from database_pkg.config.settings import database_settings
from database_pkg.config.logs import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def get_db_connection():
    db_path = str(database_settings.sqlite_path)
    logger.debug(
        f"Connecting to database at: {db_path} with app_env: {database_settings.app_env}"
    )
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_extension(filename):
    ext = filename.split(".")[-1].lower()
    if ext == "pdf":
        return "pdf"
    elif ext == "csv":
        return "csv"
    elif ext in ["xlsx", "xls"]:
        return ext
    return None
