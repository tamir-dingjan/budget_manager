"""
This in-memory database fixture lets the tests run without interacting with the real database.
"""

import pytest
import sqlite3
from budget_manager.database import create_tables


@pytest.fixture
def db_conn():
    # Create an in-memory database for testing
    connection = sqlite3.connect(":memory:")
    create_tables(connection)
    yield connection
    connection.close()
