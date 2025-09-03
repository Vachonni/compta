import argparse
import os
import requests

from prepro.utils import logger


def extract(
    file_path: str,
    base_url: str = "http://localhost:8001/extract_file",
    out_dir: str = ".",
) -> str:
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

    logger.info(f"Requesting '{file_path}' from {base_url}...")

    resp = requests.get(base_url, params={"path": file_path}, stream=True)
    resp.raise_for_status()

    # Save to disk
    filename = os.path.basename(file_path) or "downloaded_file"
    out_path = os.path.join(out_dir, filename)
    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "wb") as out_f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                out_f.write(chunk)

    logger.info(f"Saved file to {out_path}")
    return out_path


def transform(out_path: str):
    """Load a saved file at `out_path` into a pandas DataFrame.

    Supported formats: .csv, .xls, .xlsx
    """
    if not os.path.exists(out_path):
        raise FileNotFoundError(out_path)

    # Lazily import pandas; let ImportError bubble if pandas isn't installed
    import pandas as pd

    lower = out_path.lower()
    if lower.endswith(".csv"):
        df = pd.read_csv(out_path)
        logger.info(df.head())
        return
    if lower.endswith((".xls", ".xlsx")):
        df = pd.read_excel(out_path)
        logger.info(df.head())
        return

    raise ValueError(f"Unsupported file extension for DataFrame conversion: {out_path}")


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
        choices=["clean", "normalize", "split", "load"],
        required=True,
        help="Preprocessing step to execute",
    )
    parser.add_argument("--file_path", type=str, help="Path to the input file")
    args = parser.parse_args()

    if args.step == "clean":
        clean()
    elif args.step == "normalize":
        normalize()
    elif args.step == "split":
        split()
    elif args.step == "load":
        data = extract(args.file_path)
        transform(data)
