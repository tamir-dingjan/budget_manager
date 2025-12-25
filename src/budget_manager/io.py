import polars
import os


def read_csv_to_dataframe(file_path: str) -> polars.DataFrame:
    """
    Reads a CSV file and returns its contents as a Polars DataFrame.

    Args:
        file_path (str): The path to the CSV file.
    Returns:
        polars.DataFrame: The contents of the CSV file as a Polars DataFrame.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    else:
        try:
            return polars.read_csv(file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to read CSV file {file_path}: {e}") from e
            return None
