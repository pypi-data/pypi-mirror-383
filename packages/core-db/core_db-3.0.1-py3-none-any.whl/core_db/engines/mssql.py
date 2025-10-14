# -*- coding: utf-8 -*-

"""
Microsoft SQL Server Database Client Module
============================================

This module provides the MsSqlClient class for connecting to and interacting
with Microsoft SQL Server databases using the pyodbc library.
"""

import json
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pyodbc  # type: ignore

from core_db.interfaces.base import DatabaseClientException
from core_db.interfaces.sql_based import ISqlDatabaseClient


class MsSqlClient(ISqlDatabaseClient):
    """
    Client for Microsoft MsSQL connection...

    ===================================================
    How to use
    ===================================================

    .. code-block:: python

        from core_db.engines.mssql import MsSqlClient

        with MsSqlClient(
                dsn="DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=master;UID=SA;PWD=sOm3str0ngP@33w0rd;Encrypt=no",
                autocommit=True, timeout=5) as client:

            client.execute("SELECT @@VERSION AS 'version';")
            print(list(client.fetch_records()))
    ..
    """

    PLACEHOLDER = "?"

    def __init__(self, **kwargs) -> None:
        """
        Expected -> dsn, autocommit, timeout

        More information:
          - https://learn.microsoft.com/en-us/sql/connect/python/python-driver-for-sql-server?view=sql-server-ver16
          - https://learn.microsoft.com/en-us/sql/relational-databases/native-client/applications/using-connection-string-keywords-with-sql-server-native-client?view=sql-server-ver15&viewFallbackFrom=sql-server-ver16
        """

        super().__init__(**kwargs)
        self.connect_fcn = pyodbc.connect

    def connect(self) -> None:
        """
        Establish connection to Microsoft SQL Server. Uses the DSN (Data Source Name) string
        with ODBC driver to create a database connection using `pyodbc.connect()`.

        :raises DatabaseClientException: If connection fails.
        """

        if not self.connect_fcn:
            raise DatabaseClientException("Connection function not set")

        try:
            self.cxn = self.connect_fcn(
                self.cxn_parameters.pop("dsn", ""),
                **self.cxn_parameters)

        except Exception as error:
            raise DatabaseClientException(error) from error

    def test_connection(self, query: Optional[str] = None):
        """
        Test the database connection by executing a simple query.

        :param query: Optional custom query to test. Defaults to querying SQL Server version.
        :return: Result of the query execution.
        """

        query = query or "SELECT @@VERSION AS 'version';"
        return super().test_connection(query)

    def _execute(self, query, **kwargs):
        """
        Override to handle pyodbc's positional parameter requirement
        because `pyodbc` expects execute(query, params) as positional arguments,
        not execute(query, params=params) as a keyword argument.

        :param query: SQL query string to execute.
        :param kwargs: Optional keyword arguments. Supports 'params' for parameter binding.
        :return: Cursor object after execution.
        """

        params = kwargs.get("params", None)
        if params:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)

    @classmethod
    def get_merge_dml(
        cls,
        table_fqn: str,
        pk_ids: List[str],
        columns: List[str],
        records: List[Dict],
    ) -> Tuple[str, Tuple]:
        """
        Generate parameterized MERGE statement for Microsoft SQL Server. Uses
        parameter binding to prevent SQL injection attacks.

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

        # Create individual value rows for UNION ALL
        if len(records) > 1:
            # First row
            first_row = f"SELECT {', '.join([f'{cls.PLACEHOLDER} AS {col}' for col in columns])}"
            # Remaining rows
            union_rows = []
            for _ in range(1, len(records)):
                union_rows.append(f"SELECT {', '.join([cls.PLACEHOLDER for _ in columns])}")
            using_clause = f"({first_row} UNION ALL {' UNION ALL '.join(union_rows)})"
        else:
            # Single record
            using_clause = f"(SELECT {', '.join([f'{cls.PLACEHOLDER} AS {col}' for col in columns])})"

        # Building the ON clause for matching
        on_conditions = " AND ".join([f"target.{pk} = source.{pk}" for pk in pk_ids])

        # Building UPDATE SET statement
        update_columns = [col for col in columns if col not in pk_ids]
        set_statement = ", ".join([f"target.{col} = source.{col}" for col in update_columns])

        # Building INSERT statement
        insert_columns = ", ".join(columns)
        insert_values = ", ".join([f"source.{col}" for col in columns])

        # SQL construction is safe: columns are validated, values use placeholders...
        query = f"""
            MERGE INTO {table_fqn} AS target
            USING {using_clause} AS source
            ON ({on_conditions})
            WHEN MATCHED THEN
                UPDATE SET {set_statement}
            WHEN NOT MATCHED THEN
                INSERT ({insert_columns})
                VALUES ({insert_values});"""  # nosec B608

        # Extracting parameters in the correct order for each record
        params: List = []
        for record in records:
            params.extend([
                json.dumps(record[col]) if type(record[col]) in [dict, list] else record[col]
                for col in columns
            ])

        return query, tuple(params)
