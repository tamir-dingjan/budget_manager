

def test_read_csv_file_to_dataframe(tmp_path):
    from budget_manager.io import read_csv_to_dataframe
    import polars as pl
    from polars.testing import assert_frame_equal

    # Create a sample CSV file
    csv_content = "name,age\nAlice,30\nBob,25"
    csv_file = tmp_path / "test.csv"
    with open(csv_file, "w") as f:
        f.write(csv_content)

    # Read the CSV file using the function
    df = read_csv_to_dataframe(str(csv_file))

    # Expected DataFrame
    expected_df = pl.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})

    # Assert that the DataFrame matches the expected DataFrame
    assert_frame_equal(df, expected_df)
