import sqlite3
from budget_manager.database import create_tables, insert_budget, insert_transaction


def test_create_tables():
    # Create an in-memory database for testing
    # Do not use the db_conn fixture here to test table creation explicitly
    conn = sqlite3.connect(":memory:")
    create_tables(conn)
    # check if 'budgets' and 'transactions' tables exist
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='budgets';"
    )
    assert cursor.fetchone() is not None, "Table 'budgets' should exist"
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';"
    )
    assert cursor.fetchone() is not None, "Table 'transactions' should exist"
    conn.close()


def test_insert_budget(db_conn):
    name = "Groceries"
    amount = 150.0
    result = insert_budget(db_conn, name, amount)
    assert result is True, "Inserting budget should return True"

    # Verify the budget was inserted
    cursor = db_conn.cursor()
    cursor.execute("SELECT name, amount FROM budgets WHERE name=?;", (name,))
    row = cursor.fetchone()
    assert row is not None, "Inserted budget should be found in the database"
    assert row[0] == name, "Budget name should match"
    assert row[1] == amount, "Budget amount should match"


def test_insert_transaction(db_conn):
    # Insert a budget for this transaction
    budget_name = "Rent"
    budget_amount = 1000.0
    insert_budget(db_conn, budget_name, budget_amount)

    cursor = db_conn.cursor()
    cursor.execute("SELECT id FROM budgets WHERE name=?;", (budget_name,))
    budget_id = cursor.fetchone()[0]

    # Insert a transaction
    insert_transaction(db_conn, budget_id, 500.0, "2025-01-01", "Rent payment")

    # Verify the transaction was inserted
    cursor.execute(
        "SELECT budget_id, amount, date, description FROM transactions WHERE budget_id=?;",
        (budget_id,),
    )
    row = cursor.fetchone()
    assert row is not None, "Inserted transaction should be found in the database"
    assert row[0] == budget_id, "Transaction budget_id should match"
    assert row[1] == 500.0, "Transaction amount should match"
    assert row[2] == "2025-01-01", "Transaction date should match"
    assert row[3] == "Rent payment", "Transaction description should match"
