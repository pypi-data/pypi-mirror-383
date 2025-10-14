# -*- coding: utf-8 -*-

"""
Database Client Interfaces Module
==================================

This module defines abstract base classes (interfaces) for implementing
database clients with standardized methods across different
database engines.


Available Interfaces:
---------------------
  - **IDatabaseClient**: Base interface for all database clients.
  - **ISqlDatabaseClient**: Interface for SQL-based database clients with CRUD operations.
  - **DatabaseClientException**: Custom exception for database operations.

The interfaces provide:
  - Connection management with context manager support.
  - Parameterized query execution to prevent SQL injection.
  - Batch operations for efficient data manipulation.
  - Factory pattern integration for dynamic client instantiation.


Usage:
------

.. code-block:: python

    from core_db.interfaces.base import IDatabaseClient
    from core_db.interfaces.sql_based import ISqlDatabaseClient

    class MyDatabaseClient(ISqlDatabaseClient):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.connect_fcn = my_driver.connect

        def get_merge_dml(self, *args, **kwargs):
            # Implement database-specific merge logic
            pass
..


See Also:
---------
  - core_db.engines: Concrete implementations for various database systems.
"""

from .base import DatabaseClientException
from .base import IDatabaseClient
from .sql_based import ISqlDatabaseClient


__all__ = [
    "DatabaseClientException",
    "IDatabaseClient",
    "ISqlDatabaseClient",
]
