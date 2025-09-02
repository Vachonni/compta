import argparse

from prepro.utils import logger


def load(file_path):
    """Loading file from Databases"""
    logger.info(f"Loading data from {file_path}...")
    # Implementation for loading data
    data = "<loaded_data>"
    logger.info("Data loaded successfully.")
    return data


def print_data(data):
    """Printing data to console"""
    logger.info(f"Printing data: {data}")


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
        data = load(args.file_path)
        print_data(data)
