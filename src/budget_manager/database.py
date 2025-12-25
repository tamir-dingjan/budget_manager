import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "budget_manager.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    return connection


def initialise_database():
    connection = sqlite3.connect("budget_manager.db")
    create_tables(connection)
    return connection


def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            budget_id INTEGER,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY(budget_id) REFERENCES budgets(id)
        )
    """)
    connection.commit()


def get_budget_id_by_name(connection, name: str) -> int | None:
    cursor = connection.cursor()
    query = "SELECT id FROM budgets WHERE name=?"
    cursor.execute(query, (name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return None


def get_budget_amount_by_name(connection, name: str) -> float | None:
    cursor = connection.cursor()
    query = "SELECT amount FROM budgets WHERE name=?"
    cursor.execute(query, (name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return None


def insert_budget(connection, name: str, amount: float) -> bool:
    try:
        cursor = connection.cursor()
        query = "INSERT INTO budgets (name, amount) VALUES (?, ?)"
        cursor.execute(query, (name, amount))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def insert_transaction(
    connection, budget_id: int, amount: float, date: str, description: str
) -> bool:
    try:
        cursor = connection.cursor()
        query = "INSERT INTO transactions (budget_id, amount, date, description) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (budget_id, amount, date, description))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def get_all_budget_names(connection):
    cursor = connection.cursor()
    query = "SELECT name FROM budgets"
    cursor.execute(query)
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def select_transactions_by_budget_id(connection, budget_id: int):
    cursor = connection.cursor()
    query = "SELECT amount, date, description FROM transactions WHERE budget_id=?"
    cursor.execute(query, (budget_id,))
    rows = cursor.fetchall()
    return rows
