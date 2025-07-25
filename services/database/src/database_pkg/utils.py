import logging
import sqlite3

from database_pkg.config import database_settings, setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def get_db_connection():
    db_path = str(database_settings.sqlite_dev_path)
    logger.debug(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
