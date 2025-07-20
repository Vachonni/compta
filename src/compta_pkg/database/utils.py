import sqlite3

from compta_pkg.database.config.settings import database_settings


def get_db_connection():
    db_path = str(database_settings.SQLITE_DEV_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
