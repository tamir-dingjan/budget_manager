import argparse
from budget_manager.database import get_connection
from budget_manager.logic import (
    create_budget_category,
    add_transactions_from_file,
    generate_report,
    create_budget_categories_from_file,
)


def run(args=None, connection=None) -> None:
    parser = argparse.ArgumentParser(description="Budget Manager CLI")
    parser.add_argument(
        "--add-budget",
        nargs=2,
        help="Add a budget category name and its budgeted amount.",
    )
    parser.add_argument(
        "--add-budget-file",
        metavar="FILE",
        help="Add budget categories from a CSV file.",
    )
    parser.add_argument(
        "--add_transactions",
        metavar="FILE",
        help="Import transactions from a CSV file.",
    )
    parser.add_argument(
        "--report", metavar="OUT_FILE", help="Generate a report to a CSV file."
    )
    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    if connection is None:
        connection = get_connection()
        need_to_close = True
    else:
        need_to_close = False

    # Logic route based on arguments
    # Note that these routes are not exclusive, you can add budget categories, load transactions,
    # and generate a report in a single command.
    if args.add_budget:
        name, amount = args.add_budget
        print(f"Adding budget category: {name} with amount: {amount}")
        result = create_budget_category(name, amount, connection=connection)
        print(result)
    elif args.add_budget_file:
        print(f"Importing budget categories from: {args.add_budget_file}")
        result = create_budget_categories_from_file(
            args.add_budget_file, connection=connection
        )
        print("Budget category import from file not yet implemented.")

    if args.add_transactions:
        print(f"Importing transactions from: {args.add_transactions}")
        result = add_transactions_from_file(
            args.add_transactions, connection=connection
        )
        print(result)

    if args.report:
        print(f"Generating report to: {args.report}")
        result = generate_report(args.report, connection=connection)
        print(result)

    if need_to_close:
        connection.close()


if __name__ == "__main__":
    run()
