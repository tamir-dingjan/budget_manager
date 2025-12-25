import argparse
from budget_manager.logic import (
    create_budget_category,
    add_transactions_from_file,
    generate_report,
    create_budget_categories_from_file,
)


def add_budget_category():
    print("--- Add a new budget category ---")
    name = input("Enter budget name: ")
    amount = float(input("Enter budget amount: "))
    result = create_budget_category(name, amount)
    print(result)


def run() -> None:
    parser = argparse.ArgumentParser(description="Budget Manager CLI")
    parser.add_argument(
        "--add-budget",
        nargs="2",
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
    args = parser.parse_args()

    # Logic route based on arguments
    # Note that these routes are not exclusive, you can add budget categories, load transactions,
    # and generate a report in a single command.
    if args.add_budget:
        for category in args.add_budget:
            print(f"Adding budget category: {category}")
            result = create_budget_category(category[0], category[1])
            print(result)
    elif args.add_budget_file:
        print(f"Importing budget categories from: {args.add_budget_file}")
        result = create_budget_categories_from_file(args.add_budget_file)
        print("Budget category import from file not yet implemented.")

    if args.add_transactions:
        print(f"Importing transactions from: {args.add_transactions}")
        result = add_transactions_from_file(args.add_transactions)
        print(result)

    if args.report:
        print(f"Generating report to: {args.report}")
        result = generate_report(args.report)
        print(result)


if __name__ == "__main__":
    run()
