# -*- coding: utf-8 -*-

"""
MySQL Database Client Module
==============================

This module provides the MySQLClient class for connecting to and interacting
with MySQL databases using the pymysql library.
"""

import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pymysql  # type: ignore

from core_db.interfaces import DatabaseClientException
from core_db.interfaces.sql_based import ISqlDatabaseClient


class MySQLClient(ISqlDatabaseClient):
    """
    MySQL database client with parameterized query support. This client
    provides secure database operations using parameterized queries to
    prevent SQL injection attacks. It supports standard CRUD operations,
    batch inserts, upserts (MERGE), and secure SELECT/DELETE operations.

    ===================================================
    Usage Examples
    ===================================================

    Basic Connection and Query:
    ----------------------------

    .. code-block:: python

        from core_db.engines.mysql import MySQLClient

        config = {
            "host": "localhost",
            "database": "test_database",
            "user": "root",
            "password": "password"
        }

        with MySQLClient(**config) as client:
            # Test connection
            client.execute("SELECT VERSION() AS version;")
            print(client.fetch_one()[0])
    ..

    Insert Records (Batch Insert):
    -------------------------------

    .. code-block:: python

        columns = ["first_name", "last_name", "age", "email", "birthdate"]
        records = [
            {
                "first_name": "John",
                "last_name": "Doe",
                "age": 30,
                "email": "john.doe@example.com",
                "birthdate": "1994-05-15"
            },
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "age": 25,
                "email": "jane.smith@example.com",
                "birthdate": "2000-05-15"
            }
        ]

        with MySQLClient(**config) as client:
            count = client.insert_records(
                table_fqn="people",
                columns=columns,
                records=records)

            client.commit()
            print(f"Inserted {count} records")
    ..

    Select Records:
    ---------------

    .. code-block:: python

        with MySQLClient(**config) as client:
            client.select("people", columns=["first_name", "last_name", "age"])
            for record in client.fetch_records():
                print(record)
    ..

    Delete Records (Conditional):
    -----------------------------

    .. code-block:: python

        with MySQLClient(**config) as client:
            query, params = client.get_delete_dml(
                "people",
                conditionals=[{"first_name": "Jane"}])

            client.execute(query, params=params)
            client.commit()
    ..

    Upsert/Merge Records (INSERT ... ON DUPLICATE KEY UPDATE):
    -----------------------------------------------------------

    .. code-block:: python

        with MySQLClient(**config) as client:
            query, params = client.get_merge_dml(
                table_fqn="people",
                columns=columns,
                records=[
                    {
                        "first_name": "John",
                        "last_name": "Doe",
                        "age": 35,  # Updated age
                        "email": "john.doe@example.com",
                        "birthdate": "1994-05-15"
                    }
                ])

            client.execute(query, params=params)
            client.commit()
    ..

    Security Features:
    ------------------
      - All DML methods use parameterized queries with placeholders (%s)
      - Column names are validated against SQL injection patterns
      - Uses pymysql's built-in parameter binding
      - Multi-row INSERT for better performance
    """

    def __init__(self, **kwargs) -> None:
        """
        Expected -> host, user, password, database
        More information:
          - https://pymysql.readthedocs.io/en/latest/user/index.html#
          - https://pypi.org/project/PyMySQL/
        """

        super().__init__(**kwargs)
        self.epoch_to_timestamp_fcn = "FROM_UNIXTIME"
        self.connect_fcn = pymysql.connect

    def _execute(self, query: Any, **kwargs):
        """
        Execute query with parameter binding support for MySQL. Handles
        pymysql's specific parameter passing requirement where parameters
        are passed via the 'args' keyword argument.

        :param query: SQL query string to execute.
        :param kwargs: Optional keyword arguments. Supports 'params' for parameter binding.
        :return: Cursor object after execution.
        """

        if not self.cursor:
            raise DatabaseClientException("No active cursor!")

        args = kwargs
        params = kwargs.pop("params", None)
        if params:
            args["args"] = params

        return self.cursor.execute(query, **args)

    @classmethod
    def get_merge_dml(
        cls,
        table_fqn: str,
        columns: List[str],
        records: List[Dict],
        epoch_column: Optional[str] = None,
    ) -> Tuple[str, Tuple]:
        """
        Generate parameterized MERGE/UPSERT statement for MySQL using
        INSERT ... ON DUPLICATE KEY UPDATE. Uses parameter binding to
        prevent SQL injection attacks.

        :param table_fqn: Table's fully qualified name (schema.table or just table).
        :param columns: List of column names.
        :param records: List of dictionaries representing records.
        :param epoch_column: If specified, only update if this timestamp column is newer.
        :return: Tuple of (query string with placeholders, flattened parameter tuple).
        :raises ValueError: If column names contain invalid characters.
        """

        if not records:
            return "", tuple()

        cls.validate_identifier(columns)

        if epoch_column and epoch_column not in columns:
            raise ValueError(f"epoch_column '{epoch_column}' must be in columns list")

        # Build multi-row VALUES clause with placeholders
        placeholders = ", ".join(["%s" for _ in columns])
        values_rows = ", ".join([f"({placeholders})" for _ in records])

        # Building `ON DUPLICATE KEY UPDATE` statement...
        if epoch_column:
            # Only update if the new epoch value is greater
            on_duplicate = [
                f"`{col}` = IF(VALUES(`{epoch_column}`) > `{epoch_column}`, VALUES(`{col}`), `{col}`)"
                for col in columns
            ]

        else:
            on_duplicate = [f"`{col}` = VALUES(`{col}`)" for col in columns]

        # SQL construction is safe: columns are validated, values use placeholders...
        query = f"""
            INSERT INTO {table_fqn}
            ({', '.join([f'`{col}`' for col in columns])})
            VALUES {values_rows}
            ON DUPLICATE KEY UPDATE
            {', '.join(on_duplicate)}"""  # nosec B608

        # Extract and flatten parameters in the correct order
        params = []
        for record in records:
            params.extend([
                json.dumps(record[col]) if type(record[col]) in [dict, list] else record[col]
                for col in columns
            ])

        return query, tuple(params)
