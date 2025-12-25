from math import fsum
import polars as pl
from budget_manager.io import read_csv_to_dataframe
from budget_manager.database import (
    get_budget_amount_by_name,
    get_connection,
    insert_budget,
    get_budget_id_by_name,
    insert_transaction,
    get_all_budget_names,
    select_transactions_by_budget_id,
)


def create_budget_category(name: str, amount: float, connection=None) -> str:
    # Validate the name and amount
    if not name.strip():
        return "Error: Budget name cannot be empty."
    if amount <= 0:
        return "Error: Budget amount must be greater than zero."

    # Get a connection if not provided
    if connection is None:
        connection = get_connection()
        need_to_close = True
    else:
        need_to_close = False

    # Add the budget to the database
    result = insert_budget(connection, name, amount)

    if need_to_close:
        connection.close()

    if result:
        return f"Budget '{name}' with amount {amount} added successfully."
    else:
        return "Error: Failed to add budget."


def add_single_transaction(
    budget_name: str, amount: float, date: str, description: str, connection=None
) -> str:
    # Validate the inputs
    if budget_name.strip() == "":
        return "Error: Budget name cannot be empty."
    try:
        float(amount)
    except ValueError:
        return "Error: Amount must be a valid number."
    if date.strip() == "":
        return "Error: Date cannot be empty."
    if description.strip() == "":
        return "Error: Description cannot be empty."

    # Get a connection if not provided
    if connection is None:
        connection = get_connection()
        need_to_close = True
    else:
        need_to_close = False

    # Check if the budget name exists in the database
    budget_id = get_budget_id_by_name(connection, budget_name)
    if budget_id is None:
        return f"Error: Budget category '{budget_name}' does not exist."
    else:
        # Insert the transaction
        result = insert_transaction(
            connection,
            budget_id,
            amount,
            date,
            description,
        )

    if need_to_close:
        connection.close()

    if result:
        return f"Transaction for budget '{budget_name}' on date {date} with amount {amount} added successfully."
    else:
        return "Error: Failed to add transaction."


def add_transactions_from_file(file_path: str, connection=None) -> str:
    df = read_csv_to_dataframe(file_path)
    if df is None:
        return "Error: Failed to read transactions from the file."

    # Validate the transactions data
    # Each transaction must have the following fields: budget category name, amount, date
    required_columns = {"budget_name", "amount", "date", "description"}
    if not required_columns.issubset(set(df.columns)):
        return f"Error: CSV file must contain the following columns: {', '.join(required_columns)}."

    # add each transaction separately
    for row in df.iter_rows(named=True):
        budget_name = row["budget_name"]
        amount = row["amount"]
        date = row["date"]
        description = row["description"]

        result = add_single_transaction(
            budget_name, amount, date, description, connection=connection
        )
        if result.startswith("Error"):
            return f"Error adding transaction from file: {result}"

    return "All transactions from the file added successfully."


def generate_report(output_file: str, connection=None) -> str:
    summary = {
        "budget_name": [],
        "budget_amount": [],
        "total_spent": [],
        "percent_spent": [],
    }

    # Get a connection if not provided
    if connection is None:
        connection = get_connection()
        need_to_close = True
    else:
        need_to_close = False

    # Get all budget categories in the database
    budgets = get_all_budget_names(connection)

    # Collect each budget category's transactions
    for budget_name in budgets:
        budget_id = get_budget_id_by_name(connection, budget_name)
        budget_amount = get_budget_amount_by_name(connection, budget_name)
        if budget_id is None:
            return f"Error: Budget category '{budget_name}' does not exist."
        if budget_amount is None:
            return (
                f"Error: Could not retrieve amount for budget category '{budget_name}'."
            )

        # Calculate total transaction amount
        transactions = select_transactions_by_budget_id(connection, budget_id)
        total = fsum([row[0] for row in transactions])
        summary["budget_name"].append(budget_name)
        summary["budget_amount"].append(budget_amount)
        summary["total_spent"].append(total)
        summary["percent_spent"].append((total / budget_amount * 100))

    # Generate report for each budget category showing amount and % spent
    df = pl.DataFrame(
        summary,
        schema={
            "budget_name": pl.Utf8,
            "budget_amount": pl.Float64,
            "total_spent": pl.Float64,
            "percent_spent": pl.Float64,
        },
    )

    df.write_csv(output_file)

    return f"Report written to {output_file}."
