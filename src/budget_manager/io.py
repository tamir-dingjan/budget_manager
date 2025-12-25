import polars


def read_csv_to_dataframe(file_path: str) -> polars.DataFrame:
    """
    Reads a CSV file and returns its contents as a Polars DataFrame.

    Args:
        file_path (str): The path to the CSV file.
    Returns:
        polars.DataFrame: The contents of the CSV file as a Polars DataFrame.
    """
    return polars.read_csv(file_path)
