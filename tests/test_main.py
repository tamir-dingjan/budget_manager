from budget_manager.main import run
import polars as pl
from tempfile import NamedTemporaryFile


def test_cli_add_budget_category(db_conn):
    args = [
        "--add-budget",
        "Health",
        "250.0",
    ]
    run(args=args, connection=db_conn)

    # Verify that the budget category was added
    cursor = db_conn.cursor()
    cursor.execute("SELECT name, amount FROM budgets WHERE name=?;", ("Health",))
    row = cursor.fetchone()
    assert row is not None, "Budget category 'Health' should be found in the database"
    assert row[0] == "Health", "Budget name should match"
    assert row[1] == 250.0, "Budget amount should match"


def test_cli_add_budget_categories_from_file(db_conn):
    # Create a temporary CSV file with budget categories
    tmp = NamedTemporaryFile(delete=False, delete_on_close=False)
    pl.DataFrame(
        {
            "name": ["Fitness", "Travel", "Education"],
            "amount": [400.0, 800.0, 600.0],
        }
    ).write_csv(tmp.name)

    args = [
        "--add-budget-file",
        tmp.name,
    ]
    run(args=args, connection=db_conn)
    tmp.close()

    # Verify that budget categories were added
    cursor = db_conn.cursor()
    cursor.execute("SELECT name, amount FROM budgets;")
    rows = cursor.fetchall()
    budget_dict = {row[0]: row[1] for row in rows}

    assert budget_dict["Fitness"] == 400.0
    assert budget_dict["Travel"] == 800.0
    assert budget_dict["Education"] == 600.0


def test_cli_add_transactions_from_file(db_conn):
    # First, create a budget category to associate transactions with
    cursor = db_conn.cursor()
    cursor.execute(
        "INSERT INTO budgets (name, amount) VALUES (?, ?);", ("Misc", 1000.0)
    )
    cursor.execute(
        "INSERT INTO budgets (name, amount) VALUES (?, ?);", ("Rent", 3000.0)
    )
    db_conn.commit()

    # Create a temporary CSV file with transactions
    tmp = NamedTemporaryFile(delete=False, delete_on_close=False)
    pl.DataFrame(
        {
            "budget_name": ["Misc", "Misc", "Rent"],
            "amount": [50.0, 75.0, 1200.0],
            "date": ["2025-02-01", "2025-02-02", "2025-02-03"],
            "description": ["Gadget purchase", "Gift", "February rent"],
        }
    ).write_csv(tmp.name)

    args = [
        "--add-transactions",
        tmp.name,
    ]
    run(args=args, connection=db_conn)
    tmp.close()

    # Verify that transactions were added
    cursor.execute(
        """SELECT b.name, t.amount, t.date, t.description
        FROM transactions t
        JOIN budgets b ON t.budget_id = b.id;"""
    )
    rows = cursor.fetchall()
    transactions = [(row[0], row[1], row[2], row[3]) for row in rows]
    expected_transactions = [
        ("Misc", 50.0, "2025-02-01", "Gadget purchase"),
        ("Misc", 75.0, "2025-02-02", "Gift"),
        ("Rent", 1200.0, "2025-02-03", "February rent"),
    ]
    assert len(transactions) == len(expected_transactions), (
        "Number of transactions should match"
    )
    for expected in expected_transactions:
        assert expected in transactions, (
            f"Transaction {expected} should be in the database"
        )


def test_cli_generate_report(db_conn):
    # Insert budget categories and transactions
    # Create a temporary CSV file with budget categories
    tmp_budget = NamedTemporaryFile(delete=False, delete_on_close=False)
    pl.DataFrame(
        {
            "name": ["Fitness", "Travel", "Education"],
            "amount": [400.0, 800.0, 600.0],
        }
    ).write_csv(tmp_budget.name)

    cursor = db_conn.cursor()

    # Create a temporary CSV file with transactions
    tmp_transactions = NamedTemporaryFile(delete=False, delete_on_close=False)
    pl.DataFrame(
        {
            "budget_name": ["Fitness", "Travel", "Education", "Fitness", "Travel"],
            "amount": [50.0, 75.0, 1200.0, 200.0, 150.0],
            "date": [
                "2025-02-01",
                "2025-02-02",
                "2025-02-03",
                "2025-02-10",
                "2025-02-15",
            ],
            "description": [
                "Gym membership",
                "Holday",
                "Textbook",
                "Personal training",
                "Flight tickets",
            ],
        }
    ).write_csv(tmp_transactions.name)

    # Setup file handle for reporting
    tmp_report = NamedTemporaryFile(delete=False, delete_on_close=False)

    args = [
        "--add-budget-file",
        tmp_budget.name,
        "--add-transactions",
        tmp_transactions.name,
        "--report",
        tmp_report.name,
    ]
    run(args=args, connection=db_conn)
    tmp_budget.close()
    tmp_transactions.close()

    # Verify report contents
    df = pl.read_csv(tmp_report.name)
    tmp_report.close()

    assert df.shape[0] == 3, "Report should contain 3 budget categories"

    fitness_row = df.filter(pl.col("budget_name") == "Fitness")
    assert fitness_row["budget_amount"][0] == 400.0
    assert fitness_row["total_spent"][0] == 250.0
    assert fitness_row["percent_spent"][0] == 62.5
    travel_row = df.filter(pl.col("budget_name") == "Travel")
    assert travel_row["budget_amount"][0] == 800.0
    assert travel_row["total_spent"][0] == 225.0
    assert travel_row["percent_spent"][0] == 28.125
    education_row = df.filter(pl.col("budget_name") == "Education")
    assert education_row["budget_amount"][0] == 600.0
    assert education_row["total_spent"][0] == 1200.0
    assert education_row["percent_spent"][0] == 200.0
