import argparse
import os
import requests
import pandas as pd
from prepro.utils import logger, adjust_columns
from prepro.config import settings


def extract(
    databases_url: str,
    file_path: str,
):
    """Download a file from the extraction service using a GET request with a
    URL-encoded `path` query parameter (equivalent to the curl -G --data-urlencode form).

    Example curl equivalent:
      curl -G \
        --data-urlencode "path=/blob/dev/raw/2025/8/N_Revolut.csv" \
        http://localhost:8001/extract_file \
        -o N_Revolut.csv

    Returns the path to the saved file on success.
    """
    if not file_path:
        raise ValueError("file_path must be provided to extract()")

    base_url = f"{databases_url}/extract_file"
    logger.info(f"Requesting '{file_path}' from {base_url}...")

    resp = requests.get(base_url, params={"path": file_path}, stream=True)
    resp.raise_for_status()

    # Save to disk
    extracted_file = "extracted_" + os.path.basename(file_path)
    with open(extracted_file, "wb") as out_f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                out_f.write(chunk)

    logger.info(f"Saved file to {extracted_file}")


def transform(file_path: str):
    """Load a saved file at `file_path` into a pandas DataFrame.
    Supported formats: .csv, .xls, .xlsx
    """

    file_name = os.path.basename(file_path)
    extracted_file = "extracted_" + file_name
    if not os.path.exists(extracted_file):
        raise FileNotFoundError(extracted_file)

    # Load DataFrame
    if extracted_file.endswith(".csv"):
        df = pd.read_csv(extracted_file)
    elif extracted_file.endswith((".xls", ".xlsx")):
        df = pd.read_excel(extracted_file)
    else:
        raise ValueError(
            f"Unsupported file extension for DataFrame conversion: {file_path}"
        )

    # Adjust columns for standardization
    df = adjust_columns(df, file_name)

    # Save transformed DataFrame
    transformed_file = f"transformed_{file_name}"
    if transformed_file.endswith(".csv"):
        df.to_csv(transformed_file, index=False)
    elif transformed_file.endswith((".xls", ".xlsx")):
        df.to_excel(transformed_file, index=False)
    else:
        raise ValueError(f"Unsupported file extension for saving: {transformed_file}")

    logger.info(f"Transformed file saved to {transformed_file}")
    logger.info(df.head())


def load(file_path: str):
    logger.info("Loading data in SQL database...")


def clean():
    logger.info("Cleaning raw data...")


def normalize():
    logger.info("Normalizing features...")


def split():
    logger.info("Splitting dataset...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--step",
        choices=["clean", "normalize", "split", "extract", "transform", "load"],
        required=True,
        help="Preprocessing step to execute",
    )
    parser.add_argument(
        "--databases_url",
        type=str,
        default="http://localhost:8001",
        help="Base URL for the Databases service",
    )
    parser.add_argument(
        "--file_path",
        type=str,
        default="/blob/dev/raw/2025/8/N_Revolut.csv",
        help="File to extract from Databases' blob.",
    )
    args = parser.parse_args()

    if args.step == "clean":
        clean()
    elif args.step == "normalize":
        normalize()
    elif args.step == "split":
        split()
    elif args.step == "extract":
        extract(args.databases_url, args.file_path)
    elif args.step == "transform":
        transform(args.file_path)
    elif args.step == "load":
        load(args.file_path)
