# -*- coding: utf-8 -*-

"""
PostgreSQL Database Client Module
===================================

This module provides the PostgresClient class for connecting to and interacting
with PostgreSQL databases using the psycopg library.
"""

import json
from typing import Dict
from typing import List
from typing import Tuple

import psycopg

from core_db.interfaces.sql_based import ISqlDatabaseClient


class PostgresClient(ISqlDatabaseClient):
    """
    PostgreSQL database client with parameterized query support. This client
    provides secure database operations using parameterized queries to
    prevent SQL injection attacks. It supports standard CRUD
    operations, batch inserts, upserts (MERGE), and
    secure SELECT/DELETE operations.

    ===================================================
    Usage Examples
    ===================================================

    Basic Connection and Query:
    ----------------------------

    .. code-block:: python

        from core_db.engines.postgres import PostgresClient

        conninfo = "postgresql://user:password@localhost:5432/database"
        with PostgresClient(conninfo=conninfo) as client:
            # Test connection
            client.execute("SELECT version() AS version;")
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

        with PostgresClient(conninfo=conninfo) as client:
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

        with PostgresClient(conninfo=conninfo) as client:
            client.select("people", columns=["first_name", "last_name", "age"])
            for record in client.fetch_records():
                print(record)
    ..

    Delete Records (Conditional):
    -----------------------------

    .. code-block:: python

        with PostgresClient(conninfo=conninfo) as client:
            query, params = client.get_delete_dml(
                "people",
                conditionals=[
                    {"first_name": "Jane"},
                    {"last_name": "Doe"}
                ])

            client.execute(query, params=params)
            client.commit()
    ..

    Upsert/Merge Records (INSERT ... ON CONFLICT):
    -----------------------------------------------

    .. code-block:: python

        with PostgresClient(conninfo=conninfo) as client:
            query, params = client.get_merge_dml(
                table_fqn="people",
                pk_ids=["first_name"],  # Must match a UNIQUE constraint
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
      - Uses psycopg's built-in parameter binding
      - Multi-row INSERT for better performance
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize PostgreSQL client.

        :param kwargs:
            Connection parameters including 'conninfo' (connection string).
            Example: "postgresql://user:password@localhost:5432/database"

        More information:
          - https://www.psycopg.org/psycopg3/docs/
          - https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
        """

        super().__init__(**kwargs)
        self.epoch_to_timestamp_fcn = "TO_TIMESTAMP"
        self.connect_fcn = psycopg.connect

    @classmethod
    def get_merge_dml(
        cls,
        table_fqn: str,
        pk_ids: List[str],
        columns: List[str],
        records: List[Dict],
    ) -> Tuple[str, Tuple]:
        """
        Generate parameterized MERGE/UPSERT statement for PostgresSQL
        using INSERT ... ON CONFLICT. Uses parameter binding to
        prevent SQL injection attacks.

        :param table_fqn: Table's fully qualified name.
        :param pk_ids: List of primary key column names.
        :param columns: List of column names.
        :param records: List of dictionaries representing records.
        :return: Tuple of (query string with placeholders, list of parameter tuples).
        :raises ValueError: If column names contain invalid characters.
        """

        if not records:
            return "", tuple()

        cls.validate_identifier(columns + pk_ids)

        # Building parameterized VALUES statement...
        placeholders = ", ".join(["%s" for _ in columns])
        values_rows = ", ".join([f"({placeholders})" for _ in records])

        # Building UPDATE SET statement...
        update_columns = [col for col in columns if col not in pk_ids]
        set_statement = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_columns])

        # SQL construction is safe: columns are validated, values use placeholders...
        query = f"""
            INSERT INTO {table_fqn} ({', '.join(columns)})
            VALUES {values_rows}
            ON CONFLICT ({', '.join(pk_ids)}) DO UPDATE
            SET {set_statement}"""  # nosec B608

        # Extracting parameters in the correct order for each record
        params: List = []
        for record in records:
            params.extend([
                json.dumps(record[col]) if type(record[col]) in [dict, list] else record[col]
                for col in columns
            ])

        # Return flattened params as single tuple
        return query, tuple(params)
