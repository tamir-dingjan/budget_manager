# Budgeter

This is a minimal budget management and expense tracking tool, designed as a self-directed project for the Boot.dev course.

## Quick Start
To see the budget manager in action with sample data:

1. Install the package:
`pip install -e .`

2. Run the demo script:
> `cd example`

> `chmod +x run_example.sh`

> `./run_example.sh`


## Features
- Create budget categories to track expenses for different purposes.
- Enter transactions in bulk from a CSV file.
- Export spending summary reports in CSV format.

### Not yet implemented
- Filter transactions by date range and category.

## Implementation
Budgeter uses a terminal-based interface to allow the user to define budget categories, add or import transactions, view any alerts, and export summary reports. In each case, the user enters a command, the application checks the current status of the transaction database, makes any requested changes, and then responds to the user with the requested information or status updates.

The application stores transaction infromation in a local SQL database.