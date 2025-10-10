# -*- coding: utf-8 -*-

"""
Oracle Database Client Module
===============================

This module provides the OracleClient class for connecting to and interacting
with Oracle databases using the oracledb library.
"""

import json
import re
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import oracledb
from core_mixins.utils import get_batches

from core_db.interfaces.base import DatabaseClientException
from core_db.interfaces.sql_based import ISqlDatabaseClient


class OracleClient(ISqlDatabaseClient):
    """
    Client for Oracle connection...

    ===================================================
    How to use
    ===================================================

    .. code-block:: python

        from core_db.engines.oracle import OracleClient

        with OracleClient(user="...", password="...", dsn=f"{host}:{port}/{service_name}") as client:
            res = client.execute("SELECT * FROM ...")

            for x in client.fetch_all():
                print(x)
    ..
    """

    def __init__(self, **kwargs) -> None:
        """
        Expected -> user, password, dsn...

        More information:
          - https://oracle.github.io/python-oracledb/
          - https://python-oracledb.readthedocs.io/en/latest/index.html
        """

        super().__init__(**kwargs)
        self.connect_fcn = oracledb.connect

    def test_connection(self, query: Optional[str] = None):
        """
        Test the database connection by executing a simple query.

        :param query: Optional custom query to test. Defaults to querying Oracle version.
        :return: Result of the query execution.
        """

        if not query:
            query = 'SELECT * FROM "V$VERSION"'

        return super().test_connection(query)

    @staticmethod
    def _convert_value(value: Any) -> Any:
        """
        Convert Python values to Oracle-compatible types.

        :param value: The value to convert.
        :return: Converted value.
        """

        if type(value) in [dict, list]:
            return json.dumps(value)

        elif isinstance(value, str):
            # Trying to parse date strings in ISO format...
            if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                try:
                    return datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    return value

            elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', value):
                try:
                    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return value

        return value

    def _execute(self, query: Any, **kwargs):
        """
        Override execute to handle Oracle's parameter format requirements,
        because Oracle's oracledb driver expects parameters as a list passed as
        the second positional argument, not as a keyword argument.
        """

        if not self.cursor:
            raise DatabaseClientException("No active cursor!")

        params = kwargs.pop("params", None)
        if params:
            # Converting tuple to list and apply value conversions...
            if isinstance(params, tuple):
                params = [self._convert_value(p) for p in params]

            elif isinstance(params, list):
                params = [self._convert_value(p) for p in params]

            return self.cursor.execute(query, params, **kwargs)

        return self.cursor.execute(query, **kwargs)

    def insert_records(
        self,
        table_fqn: str,
        columns: List[str],
        records: List[Dict],
        records_per_request: int = 500,
    ) -> int:
        """
        Insert records using Oracle's executemany for better performance
        and proper type handling.

        :param table_fqn: Table's fully qualified name (FQN).
        :param columns: List of column names to insert into.
        :param records: List of dictionaries representing records to insert.
        :param records_per_request: Number of records to insert per batch.
        :return: Total number of inserted records.
        :raises DatabaseClientException: If insertion fails.
        """

        if not records:
            return 0

        if not self.cxn:
            raise DatabaseClientException("There is not an active connection!")

        try:
            # Ensure cursor exists
            if not self.cursor:
                self.cursor = self.cxn.cursor()

            self.validate_identifier(columns)

            # Building single-row INSERT with placeholders...
            placeholders = ", ".join([f":{i + 1}" for i in range(len(columns))])
            
            # SQL construction is safe: columns are validated, values use placeholders...
            query = f"INSERT INTO {table_fqn} ({', '.join(columns)}) VALUES ({placeholders})"  # nosec B608

            total = 0
            for chunk in get_batches(records, records_per_request):
                # Convert records to list of lists for executemany
                params_list = []
                for record in chunk:
                    row: List[Any] = []
                    for col in columns:
                        value = record[col]
                        # Handle different data types
                        if type(value) in [dict, list]:
                            row.append(json.dumps(value))
                        elif isinstance(value, str):
                            # Try to parse date strings in ISO format
                            if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                                try:
                                    row.append(datetime.strptime(value, '%Y-%m-%d').date())
                                except ValueError:
                                    row.append(value)
                            elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', value):
                                try:
                                    row.append(datetime.strptime(value, '%Y-%m-%d %H:%M:%S'))
                                except ValueError:
                                    row.append(value)
                            else:
                                row.append(value)
                        else:
                            row.append(value)
                    params_list.append(row)

                self.cursor.executemany(query, params_list)
                total += self.cursor.rowcount

            return total

        except Exception as error:
            raise DatabaseClientException(error) from error

    @classmethod
    def _get_conditional_statements(
        cls,
        conditionals: Optional[List[Dict]] = None,
    ) -> Tuple[List, List]:
        """
        Helper function to generate the conditions and params and reuse it
        into other implementations. Override if required by a
        specific engine.
        """

        condition_parts = []
        param_counter = 1
        params = []

        if conditionals:
            for conditional in conditionals:
                keys = list(conditional.keys())
                condition_part = " AND ".join([f"{key} = :{param_counter + i}" for i, key in enumerate(keys)])
                condition_parts.append(f"({condition_part})")
                params.extend([conditional[key] for key in keys])
                param_counter += len(keys)

        return condition_parts, params

    @classmethod
    def get_insert_dml(
        cls,
        table_fqn: str,
        columns: List[str],
        records: List[Dict],
    ) -> Tuple[str, Tuple]:
        """
        Generate a parameterized INSERT statement for Oracle. Uses Oracle's
        named parameter syntax (:1, :2, etc.) and parameter binding
        to prevent SQL injection attacks.

        :param table_fqn: Table's fully qualified name (FQN).
        :param columns: List of column names to insert into.
        :param records: List of dictionaries representing records to insert.
        :return: Tuple of (query string with placeholders, flattened parameter tuple).
        :raises ValueError: If column names contain invalid characters.
        """

        if not records:
            return "", tuple()

        cls.validate_identifier(columns)
        insert_statements = []

        # Building multi-row INSERT ALL statement with Oracle syntax...
        for i, record in enumerate(records):
            offset = i * len(columns)
            placeholders = ", ".join([f":{offset + j + 1}" for j in range(len(columns))])
            insert_statements.append(f"INTO {table_fqn} ({', '.join(columns)}) VALUES ({placeholders})")

        # SQL construction is safe: columns are validated, values use placeholders...
        query = f"INSERT ALL\n  " + "\n  ".join(insert_statements) + "\nSELECT 1 FROM DUAL"  # nosec B608

        # Extract and flatten parameters in the correct order
        params = []
        for record in records:
            params.extend([
                json.dumps(record[col]) if type(record[col]) in [dict, list] else record[col]
                for col in columns
            ])

        return query, tuple(params)

    @classmethod
    def get_merge_dml(
        cls,
        table_fqn: str,
        pk_ids: List[str],
        columns: List[str],
        records: List[Dict],
    ) -> Tuple[str, Tuple]:
        """
        Generate parameterized MERGE statement for Oracle. Uses parameter
        binding to prevent SQL injection attacks.

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

        # Column aliases for the source (first record)
        source_columns = ", ".join([f":{i + 1} AS {col}" for i, col in enumerate(columns)])

        # Building the single-row source for the first record - SQL construction is safe: columns validated, values use placeholders
        first_select = f"SELECT {source_columns} FROM DUAL"  # nosec B608

        # Building the USING clause with UNION ALL for multiple records
        if len(records) > 1:
            union_selects = []
            for i in range(1, len(records)):
                offset = i * len(columns)
                union_columns = ", ".join([f":{offset + j + 1} AS {col}" for j, col in enumerate(columns)])
                union_selects.append(f"SELECT {union_columns} FROM DUAL")  # nosec B608
            using_clause = f"({first_select} UNION ALL {' UNION ALL '.join(union_selects)})"
        else:
            using_clause = f"({first_select})"

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
            MERGE INTO {table_fqn} target
            USING {using_clause} source
            ON ({on_conditions})
            WHEN MATCHED THEN
                UPDATE SET {set_statement}
            WHEN NOT MATCHED THEN
                INSERT ({insert_columns})
                VALUES ({insert_values})"""  # nosec B608

        # Extracting parameters in the correct order for each record...
        params: List = []
        for record in records:
            params.extend([
                json.dumps(record[col]) if type(record[col]) in [dict, list] else record[col]
                for col in columns
            ])

        return query, tuple(params)
