import argparse
import os
import requests
import pandas as pd
from prepro.utils import (
    logger,
    map_columns_to_standard,
    adjust_columns,
    load_to_postgres,
)
from prepro.config.settings import settings


# Create temporary directory for ETL files
TMP_ETL_DIR = os.path.join(settings.root_dir, "tmp_etl")
os.makedirs(TMP_ETL_DIR, exist_ok=True)


def extract(
    databases_url: str,
    file_path: str,
):
    """Download a file from the extraction service and save it locally.

    This function issues an HTTP GET to ``{databases_url}/extract_file`` with
    a URL-encoded ``path`` query parameter (equivalent to curl -G
    --data-urlencode). The response body is streamed to disk and saved as
    ``extracted_<basename(file_path)>``.

    Note: this function performs side-effects (writes a file and logs) and
    does not return a value. On HTTP errors ``requests.HTTPError`` will be
    raised by ``resp.raise_for_status()``.

    Example curl equivalent:
      curl -G \
        --data-urlencode "path=/blob/dev/raw/2025/8/N_Revolut.csv" \
        BLOB_URL/extract_file \
        -o N_Revolut.csv

    Raises:
        ValueError: if ``file_path`` is falsy.
        requests.HTTPError: if the GET request returns a non-2xx status.
    """
    if not file_path:
        raise ValueError("file_path must be provided to extract()")

    base_url = f"{databases_url}/extract_file"
    logger.info(f"Requesting '{file_path}' from {base_url}...")

    resp = requests.get(base_url, params={"path": file_path}, stream=True)
    resp.raise_for_status()

    # Save to disk
    extracted_file = "extracted_" + os.path.basename(file_path)
    extracted_file_path = os.path.join(TMP_ETL_DIR, extracted_file)

    with open(extracted_file_path, "wb") as out_f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                out_f.write(chunk)

    logger.info(f"Saved file to {extracted_file_path}")


def transform(file_path: str):
    """Load a previously extracted file, normalize columns and save a transformed file.

    Expects a file previously downloaded by :func:`extract` and saved as
    ``extracted_<basename(file_path)>``. The file is read into a pandas
    DataFrame (supports ``.csv``, ``.xls``, ``.xlsx``), then column names are
    mapped to standard names via :func:`map_columns_to_standard` and adjusted
    for database storage via :func:`adjust_columns`.

    The transformed DataFrame is written to ``transformed_<basename(file_path)>``
    and a small preview is logged. This function performs side-effects and
    does not return the DataFrame.

    Raises:
        FileNotFoundError: if the expected extracted file does not exist.
        ValueError: if the file extension is unsupported for reading or writing.
    """

    file_name = os.path.basename(file_path)
    extracted_file = "extracted_" + file_name
    extracted_file_path = os.path.join(TMP_ETL_DIR, extracted_file)

    if not os.path.exists(extracted_file_path):
        raise FileNotFoundError(extracted_file_path)

    # Load DataFrame
    if extracted_file_path.endswith(".csv"):
        df = pd.read_csv(extracted_file_path)
    elif extracted_file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(extracted_file_path)
    else:
        raise ValueError(
            f"Unsupported file extension for DataFrame conversion: {file_path}"
        )

    # Map columns to standard names
    df = map_columns_to_standard(df)

    # Adjust columns for DB standardization
    df = adjust_columns(df, file_name)

    # Save transformed DataFrame
    transformed_file = f"transformed_{file_name}"
    transformed_file_path = os.path.join(TMP_ETL_DIR, transformed_file)

    if transformed_file_path.endswith(".csv"):
        df.to_csv(transformed_file_path, index=False)
    elif transformed_file_path.endswith((".xls", ".xlsx")):
        df.to_excel(transformed_file_path, index=False)
    else:
        raise ValueError(f"Unsupported file extension for saving: {transformed_file}")

    logger.info(f"Transformed file saved to {transformed_file_path}")
    logger.info(df.head())


def load(file_path: str):
    """Load a transformed file into Postgres and clean up temporary files.

    Looks for ``transformed_<basename(file_path)>`` and, if present, calls
    :func:`load_to_postgres` to load it into the database. After a successful
    load this function attempts to delete the temporary files
    ``extracted_<basename>`` and ``transformed_<basename>``. If the transformed
    file is missing the function logs an error and returns early.
    """

    logger.info("Loading data in SQL database...")
    # Insure transformed file exists
    file_name = os.path.basename(file_path)
    transformed_file = f"transformed_{file_name}"
    transformed_file_path = os.path.join(TMP_ETL_DIR, transformed_file)
    if not os.path.exists(transformed_file_path):
        logger.error(f"Transformed file not found: {transformed_file_path}")
        return

    # Load to Postgres
    load_to_postgres(transformed_file_path)

    # Delete temporary files created after loading
    extracted_file = f"extracted_{file_name}"
    extracted_file_path = os.path.join(TMP_ETL_DIR, extracted_file)
    for f in [extracted_file_path, transformed_file_path]:
        if os.path.exists(f):
            os.remove(f)
            logger.info(f"Deleted file: {f}")
        else:
            logger.info(f"File not found, skipping delete: {f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--step",
        choices=["etl", "extract", "transform", "load"],
        required=True,
        help="Preprocessing step to execute",
    )
    parser.add_argument(
        "--databases_url",
        type=str,
        default=settings.blob_url,
        help="Base URL for the Databases service",
    )
    parser.add_argument(
        "--file_path",
        type=str,
        default="/blob/dev/raw/2025/8/N_Revolut.csv",
        help="File to extract from Databases' blob.",
    )
    args = parser.parse_args()

    if args.step == "etl":
        extract(args.databases_url, args.file_path)
        transform(args.file_path)
        load(args.file_path)
    elif args.step == "extract":
        extract(args.databases_url, args.file_path)
    elif args.step == "transform":
        transform(args.file_path)
    elif args.step == "load":
        load(args.file_path)
