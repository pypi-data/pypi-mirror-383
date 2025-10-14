# -*- coding: utf-8 -*-

"""
Snowflake Data Warehouse Client Module
========================================

This module provides the SnowflakeClient class for connecting to and interacting
with Snowflake Data Warehouse using the snowflake-connector-python library.
"""

import json
import re
from datetime import date
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import overload

import snowflake.connector

from core_db.interfaces.sql_based import ISqlDatabaseClient


class SnowflakeClient(ISqlDatabaseClient):
    """
    Client for Snowflake Data Warehouse connection. This client provides
    secure database operations using parameterized queries and input validation
    to prevent SQL injection attacks. It supports standard
    CRUD operations, batch inserts, and upserts (MERGE).

    ===================================================
    Usage Examples
    ===================================================

    Basic Connection and Query:
    ----------------------------

    .. code-block:: python

        from core_db.engines.snowflake_ import SnowflakeClient

        config = {
            "user": "username",
            "password": "password",
            "account": "account_name",
            "warehouse": "warehouse_name",
            "database": "database_name",
            "schema": "schema_name"
        }

        with SnowflakeClient(**config) as client:
            client.execute("SELECT CURRENT_VERSION();")
            print(client.fetch_one())
    ..

    Security Features:
    ------------------
      - Validates all SQL identifiers (table/column names) against injection patterns
      - Escapes string values to prevent SQL injection
      - Supports parameterized queries where applicable
      - Validates fully qualified names (schema.table)
    """

    TYPE_MAPPER = {
        int: "INTEGER",
        float: "DOUBLE",
        str: "VARCHAR",
        bool: "BOOLEAN",
        dict: "OBJECT",
        list: "VARIANT"
    }

    VALID_IDENTIFIER = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$")

    def __init__(self, **kwargs) -> None:
        """
        :param kwargs:
            * user: Username.
            * host: Hostname.
            * account: Account name.
            * password: Password.
            * warehouse: Warehouse.
            * database: Database.
            * schema: Schema.
            * role: Role.

        To connect using OAuth, the connection string must include the authenticator parameter set
        to oauth and the token parameter set to the oauth_access_token.
        https://docs.snowflake.com/en/user-guide/python-connector-example.html#connecting-with-oauth

        :param authenticator="oauth"
        :param token="oauth_access_token"
        """

        super().__init__(**kwargs)
        self.connect_fcn = snowflake.connector.connect
        self.epoch_to_timestamp_fcn = "TO_TIMESTAMP"

    def test_connection(self, query: Optional[str] = None):
        """
        Test the database connection by executing a simple query.

        :param query: Optional custom query to test. Defaults to querying Snowflake version.
        :return: Result of the query execution.
        """

        if not query:
            query = "SELECT current_version();"
        return super().test_connection(query)

    @classmethod
    def get_insert_dml(cls, table_fqn: str, columns: List, records: List[Dict]):
        if not records:
            return "", tuple()

        # Validate table name and columns...
        cls.validate_identifier([table_fqn] + columns)

        select_statement = ", ".join([
            f"PARSE_JSON(Column{pos + 1}) AS {column}"
            if isinstance(records[0][column], list) or isinstance(records[0][column], dict)
            else f"Column{pos + 1} AS {column}"
            for pos, column in enumerate(columns)
        ])

        # Explicitly specify columns to insert into (important for tables with auto-increment columns)
        columns_list = ", ".join(columns)

        # SQL construction is safe: identifiers are validated, values are escaped...
        query = f"""
            INSERT INTO {table_fqn} ({columns_list})
            SELECT {select_statement}
            FROM VALUES {', '.join(cls._get_values_statement(columns, records))};"""  # nosec B608

        return query, tuple()

    @classmethod
    @overload
    def get_merge_dml(
        cls,
        target: str,
        columns: List[str],
        pk_ids: List[str],
        records: List[Dict],
        source: Optional[str] = None,
        epoch_column: Optional[str] = None,
    ) -> Tuple[str, Tuple]:
        """ Use this one when the source is a table """

    @classmethod
    @overload
    def get_merge_dml(
        cls,
        target: str,
        columns: List[str],
        pk_ids: List[str],
        records: Optional[List[Dict]] = None,
        source: Optional[str] = None,
        epoch_column: Optional[str] = None,
    ) -> Tuple[str, Tuple]:
        """ Use this one when the source is a list of records """

    @classmethod
    def get_merge_dml(
        cls,
        target: str,
        columns: List[str],
        pk_ids: List[str],
        records: Optional[List[Dict]] = None,
        source: Optional[str] = None,
        epoch_column: Optional[str] = None,
    ) -> Tuple[str, Tuple]:

        # Validate target table name, pk_ids and columns...
        cls.validate_identifier([target] + pk_ids + columns)

        if epoch_column:
            cls.validate_identifier([epoch_column])

        source_key = source or "source"

        # If source is provided externally, validate it (basic check)
        if source and source != "source":
            # For table sources, validate the identifier
            # Note: This is a simplified check. For complex sources, more validation may be needed.
            cls.validate_identifier([source_key])

        on_sts = " AND ".join([f"{target}.{key} = {source_key}.{key}" for key in pk_ids])
        matched_and = f"AND {source_key}.{epoch_column} > {target}.{epoch_column} " if epoch_column else ""

        all_columns = pk_ids + columns
        if epoch_column:
            all_columns.extend([epoch_column])

        all_columns = sorted(set(all_columns))
        set_statement = [f"{key} = {source_key}.{key}" for key in all_columns if key not in pk_ids]

        source = source
        if not source:
            if not records:
                return "", tuple()
            
            # Use all_columns (sorted) to ensure VALUES match the column order in the source definition
            # SQL construction is safe: identifiers are validated, values are escaped...
            source = f"""(
                    SELECT * FROM (
                        VALUES
                        {', '.join(cls._get_values_statement(all_columns, records))}
                    ) AS source({', '.join(all_columns)})
                ) AS source"""  # nosec B608

        # SQL construction is safe: identifiers are validated, values are escaped...
        query = f"""
            MERGE INTO {target}
            USING {source}
            ON {on_sts}
            WHEN MATCHED {matched_and}THEN
            UPDATE SET {', '.join(set_statement)}
            WHEN NOT MATCHED THEN
            INSERT ({', '.join(all_columns)})
            VALUES ({', '.join([f'{source_key}.{key}' for key in all_columns])});"""  # nosec B608

        return query, tuple()

    @classmethod
    def _get_values_statement(cls, columns: List[str], records: List[Dict]) -> List:
        """
        Generate VALUES clause with properly escaped values.

        :param columns: List of column names.
        :param records: List of record dictionaries.
        :return: List of value tuples as strings.
        """

        values = []
        for record in records:
            tmp = []
            for key in columns:
                value = record[key]

                if isinstance(value, list) or isinstance(value, dict):
                    # JSON values need to be escaped
                    json_str = json.dumps(value)
                    escaped_json = cls._escape_string_value(json_str)
                    tmp.append(f"'{escaped_json}'")
                
                elif isinstance(value, str):
                    # String values need escaping
                    escaped_str = cls._escape_string_value(value)
                    tmp.append(f"'{escaped_str}'")
                
                elif value is None:
                    # NULL values
                    tmp.append("NULL")
                
                elif isinstance(value, (date, datetime)):
                    # Date and datetime values need to be converted to strings and quoted
                    str_value = str(value)
                    escaped_str = cls._escape_string_value(str_value)
                    tmp.append(f"'{escaped_str}'")
                
                else:
                    # Numeric and boolean values (safe, no escaping needed)
                    tmp.append(str(value))

            values.append(f"({', '.join(tmp)})")

        return values
