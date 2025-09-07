import pandas as pd
import logging

from prepro.config.logs import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def adjust_columns(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    """
    Adjust columns for standardization:
    - Add 'Executor' column with first letter of file_name
    - Remove 'Balance' column if it exists
    - Keep only rows where 'State' == 'COMPLETED', then remove column 'State'
    """
    df["Executor"] = file_name[0] if file_name else ""
    if "Balance" in df.columns:
        df = df.drop(columns=["Balance"])
    if "State" in df.columns:
        df = df[df["State"] == "COMPLETED"]
        df = df.drop(columns=["State"])
    return df
