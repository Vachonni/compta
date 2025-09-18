import logging

import pandas as pd
from sqlalchemy import create_engine, text

from prepro.config.logs import setup_logging
from prepro.config.settings import settings


setup_logging()
logger = logging.getLogger(__name__)


def map_columns_to_standard(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns in the DataFrame to standardized names based on COLUMN_EQUIVALENTS from settings.
    Columns without a mapping are dropped, and a warning is logged for each dropped column.
    """
    mapping = {}
    unmapped = []
    for col in df.columns:
        col_clean = col.strip().lower()
        found = False
        for std_col, equivalents in settings.COLUMN_EQUIVALENTS.items():
            for equiv in equivalents:
                if col_clean == equiv.strip().lower():
                    mapping[col] = std_col
                    found = True
                    break
            if found:
                break
        if not found:
            unmapped.append(col)
    if unmapped:
        logger.warning(f"Dropping columns with no mapping: {unmapped}")
        df = df.drop(columns=unmapped)
    return df.rename(columns=mapping)


def adjust_columns(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    """
    Standardize and filter DataFrame columns for further processing.
    - Adds an 'Executor' column using the first letter of the file name.
    - Removes the 'Balance' column if present.
    - Filters rows to keep only those where 'State' is 'COMPLETED' or 'TERMINÉ', then drops the 'State' column.
    """
    df["Executor"] = file_name[0] if file_name else ""
    if "Balance" in df.columns:
        df = df.drop(columns=["Balance"])
    if "State" in df.columns:
        df = df[df["State"].isin(["COMPLETED", "TERMINÉ"])]
        df = df.drop(columns=["State"])
    return df


def load_to_postgres(transformed_file: str):
    """
    Load a transformed file into the Postgres 'transactions' table with upsert logic.
    The upsert is based on ("Started Date", "Completed Date", "Description", "Amount").
    If a row with the same key exists, update relevant fields; otherwise, insert a new row.
    """
    # Establish database connection (update db_url as needed for your environment)
    db_url = "postgresql://postgres@localhost/compta_perso"
    engine = create_engine(db_url)

    # Load the DataFrame from the provided file
    if transformed_file.endswith(".csv"):
        df = pd.read_csv(transformed_file)
    elif transformed_file.endswith((".xls", ".xlsx")):
        df = pd.read_excel(transformed_file)
    else:
        raise ValueError(f"Unsupported file extension for loading: {transformed_file}")

    # Insert or update each row in the transactions table
    with engine.begin() as conn:
        for _, row in df.iterrows():
            stmt = text(
                """
                INSERT INTO transactions (
                    "Started Date", "Completed Date", "Type", "Product", "Description", "Amount", "Fee", "Currency", "Executor", "Timestamp"
                ) VALUES (
                    :started_date, :completed_date, :type, :product, :description, :amount, :fee, :currency, :executor, CURRENT_TIMESTAMP
                )
                ON CONFLICT ("Started Date", "Completed Date", "Description", "Amount") DO UPDATE SET
                    "Type" = EXCLUDED."Type",
                    "Product" = EXCLUDED."Product",
                    "Fee" = EXCLUDED."Fee",
                    "Currency" = EXCLUDED."Currency",
                    "Executor" = EXCLUDED."Executor",
                    "Timestamp" = CURRENT_TIMESTAMP
                -- The id column is not updated and remains unchanged on conflict
                """
            )
            conn.execute(
                stmt,
                {
                    "started_date": row["Started Date"],
                    "completed_date": row["Completed Date"],
                    "type": row["Type"],
                    "product": row["Product"],
                    "description": row["Description"],
                    "amount": row["Amount"],
                    "fee": row["Fee"],
                    "currency": row["Currency"],
                    "executor": row["Executor"],
                },
            )
    logger.info(f"Loaded {len(df)} rows into transactions table.")
