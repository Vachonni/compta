import sqlite3
from pathlib import Path

import pandas as pd

from compta_pkg.database.config.settings import database_settings


def excel_to_sqlite(excel_path: Path, sqlite_path: Path, table_name: str) -> None:
    """
    Load all sheets from an Excel file into a SQLite database.
    """
    # Load all sheets into a dict of DataFrames
    dfs: dict[str, pd.DataFrame] = pd.read_excel(excel_path, sheet_name=None)

    # Connect to SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect(sqlite_path)

    # Write each sheet to its own table
    for sheet, df in dfs.items():
        # Use sheet name as table name
        df.to_sql(sheet, conn, if_exists="replace", index=False)
        print(
            f"Sheet '{sheet}' from {excel_path} loaded into {sqlite_path} (table: {sheet})"
        )

    conn.close()


if __name__ == "__main__":
    # table_name argument is ignored when loading all sheets
    excel_to_sqlite(
        database_settings.EXCEL_PATH,
        database_settings.SQLITE_DEV_PATH,
        database_settings.TABLE_NAME,
    )
