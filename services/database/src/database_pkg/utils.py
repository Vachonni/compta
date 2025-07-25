import sqlite3

from database_pkg.config import database_settings


def get_db_connection():
    db_path = str(database_settings.sqlite_dev_path)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
