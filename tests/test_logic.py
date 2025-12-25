import polars as pl
from tempfile import NamedTemporaryFile
from budget_manager.logic import (
    create_budget_category,
    create_budget_categories_from_file,
    add_single_transaction,
    add_transactions_from_file,
    generate_report,
)


def test_create_budget_category(db_conn):
    # Test with valid inputs
    result = create_budget_category("Entertainment", 200.0, connection=db_conn)
    assert "added successfully" in result

    # Test with empty name
    result = create_budget_category("", 100.0, connection=db_conn)
    assert result == "Error: Budget name cannot be empty."

    # Test with name containing only spaces
    result = create_budget_category("   ", 100.0, connection=db_conn)
    assert result == "Error: Budget name cannot be empty."

    # Test with zero amount
    result = create_budget_category("Utilities", 0, connection=db_conn)
    assert result == "Error: Budget amount must be greater than zero."

    # Test with negative amount
    result = create_budget_category("Rent", -500.0, connection=db_conn)
    assert result == "Error: Budget amount must be greater than zero."


def test_create_budget_categories_from_file(db_conn):
    # Create a temporary CSV file with budget categories
    tmp = NamedTemporaryFile(delete=False, delete_on_close=False)
    pl.DataFrame(
        {
            "name": ["Groceries", "Transport", "Entertainment"],
            "amount": [300.0, 100.0, 150.0],
        }
    ).write_csv(tmp.name)

    # Test creating budget categories from the file
    result = create_budget_categories_from_file(tmp.name, connection=db_conn)
    tmp.close()

    assert result == "All budget categories from the file added successfully."

    # Verify that budget categories were added
    cursor = db_conn.cursor()
    cursor.execute("SELECT name, amount FROM budgets;")
    rows = cursor.fetchall()
    budget_dict = {row[0]: row[1] for row in rows}

    assert budget_dict["Groceries"] == 300.0
    assert budget_dict["Transport"] == 100.0
    assert budget_dict["Entertainment"] == 150.0


def test_add_single_transaction(db_conn):
    # First, insert a budget category to reference
    create_budget_category("Groceries", 300.0, connection=db_conn)

    # Test with valid inputs
    result = add_single_transaction(
        "Groceries", 50.0, "2024-01-15", "Weekly groceries", connection=db_conn
    )
    assert "added successfully" in result

    # Test with empty budget name
    result = add_single_transaction(
        "", 50.0, "2024-01-15", "Weekly groceries", connection=db_conn
    )
    assert result == "Error: Budget name cannot be empty."

    # Test with non-numeric amount
    result = add_single_transaction(
        "Groceries", "fifty", "2024-01-15", "Weekly groceries", connection=db_conn
    )
    assert result == "Error: Amount must be a valid number."

    # Test with empty date
    result = add_single_transaction(
        "Groceries", 50.0, "", "Weekly groceries", connection=db_conn
    )
    assert result == "Error: Date cannot be empty."

    # Test with empty description
    result = add_single_transaction(
        "Groceries", 50.0, "2024-01-15", "", connection=db_conn
    )
    assert result == "Error: Description cannot be empty."

    # Test with non-existing budget category
    result = add_single_transaction(
        "NonExistingBudget", 50.0, "2024-01-15", "Some description", connection=db_conn
    )
    assert result == "Error: Budget category 'NonExistingBudget' does not exist."


def test_add_transactions_from_file(db_conn):
    # Insert budget categories to reference
    create_budget_category("Groceries", 300.0, connection=db_conn)
    create_budget_category("Entertainment", 150.0, connection=db_conn)

    # Make temporary csv file
    tmp = NamedTemporaryFile(delete=False, delete_on_close=False)
    pl.DataFrame(
        {
            "budget_name": ["Groceries", "Entertainment"],
            "amount": [75.0, 120.0],
            "date": ["2024-02-01", "2024-02-02"],
            "description": ["Grocery shopping", "Concert tickets"],
        }
    ).write_csv(tmp.name)

    # Test adding transactions from the file
    result = add_transactions_from_file(tmp.name, connection=db_conn)
    tmp.close()

    assert result == "All transactions from the file added successfully."

    # Verify that transactions were added
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions;")
    count = cursor.fetchone()[0]
    assert count == 2, "There should be 2 transactions in the database."

    cursor.execute("SELECT budget_id, amount, date, description FROM transactions;")
    rows = cursor.fetchall()
    assert rows[0][1] == 75.0
    assert rows[0][2] == "2024-02-01"
    assert rows[0][3] == "Grocery shopping"
    assert rows[1][1] == 120.0
    assert rows[1][2] == "2024-02-02"
    assert rows[1][3] == "Concert tickets"


def test_generate_report(db_conn):
    # Insert budget categories and transactions
    create_budget_category("Groceries", 300.0, connection=db_conn)
    create_budget_category("Entertainment", 150.0, connection=db_conn)

    add_single_transaction(
        "Groceries", 50.0, "2024-01-15", "Weekly groceries", connection=db_conn
    )
    add_single_transaction(
        "Groceries", 75.0, "2024-01-22", "Monthly bulk shopping", connection=db_conn
    )
    add_single_transaction(
        "Entertainment", 120.0, "2024-01-20", "Concert tickets", connection=db_conn
    )

    # Generate report
    tmp = NamedTemporaryFile(delete=False, delete_on_close=False)
    result = generate_report(tmp.name, connection=db_conn)

    assert result == f"Report written to {tmp.name}."

    # Validate the contents of the report
    df = pl.read_csv(tmp.name)
    assert df.shape[0] == 2, "Report should contain 2 budget categories."

    groceries_row = df.filter(pl.col("budget_name") == "Groceries")
    assert groceries_row["total_spent"][0] == 125.0
    assert groceries_row["percent_spent"][0] == (125.0 / 300.0 * 100)

    entertainment_row = df.filter(pl.col("budget_name") == "Entertainment")
    assert entertainment_row["total_spent"][0] == 120.0
    assert entertainment_row["percent_spent"][0] == (120.0 / 150.0 * 100)
