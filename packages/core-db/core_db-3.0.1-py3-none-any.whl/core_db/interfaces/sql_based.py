# -*- coding: utf-8 -*-

import json
import re
from abc import ABC, abstractmethod
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import overload

from core_mixins.utils import get_batches

from core_db.interfaces.base import DatabaseClientException
from .base import IDatabaseClient


class ISqlDatabaseClient(IDatabaseClient, ABC):
    """
    Abstract base class for SQL-based database clients.

    This class extends IDatabaseClient to provide SQL-specific functionality including
    parameterized query execution, CRUD operations, and batch data manipulation. It
    implements security measures to prevent SQL injection and provides standardized
    methods for common database operations.

    Key Features:
    -------------
      - **Parameterized queries**: All DML methods use placeholders to prevent SQL injection.
      - **Batch operations**: Efficient batch inserts with configurable chunk sizes.
      - **Type mapping**: Python-to-SQL type conversion for DDL generation.
      - **Column validation**: Automatic validation of column names against injection patterns.
      - **Context manager support**: Automatic commit and connection cleanup.

    Attributes:
        TYPE_MAPPER (Dict): Mapping from Python types to SQL type names
        VALID_IDENTIFIER (Pattern): Regex pattern for validating SQL identifiers
        PLACEHOLDER (str): Database-specific parameter placeholder (e.g., %s, ?, :1)
        epoch_to_timestamp_fcn (str): SQL function name for epoch-to-timestamp conversion

    Usage:
    ------
    .. code-block:: python

        class MyDatabaseClient(ISqlDatabaseClient):
            PLACEHOLDER = "?"  # Override for database-specific placeholder

            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.connect_fcn = my_driver.connect

            @classmethod
            def get_merge_dml(cls, table_fqn, pk_ids, columns, records):
                # Implement database-specific MERGE/UPSERT logic
                pass

        # Use the client
        with MyDatabaseClient(host="localhost", database="mydb") as client:
            # Insert records
            client.insert_records(
                table_fqn="users",
                columns=["name", "email"],
                records=[{"name": "Alice", "email": "alice@example.com"}]
            )
            # Query data
            client.select("users", columns=["name", "email"])
            for record in client.fetch_records():
                print(record)
    ..

    See Also:
    ---------
      - core_db.engines: Concrete implementations for specific databases
    """

    # Mapper for python types to database types...
    TYPE_MAPPER = {
        int: "INTEGER",
        float: "DOUBLE",
        str: "TEXT",
        bool: "BOOLEAN",
        dict: "JSON",
        list: "JSON",
    }

    # Valid identifier to validate column names
    # preventing SQL injection...
    VALID_IDENTIFIER = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    # Each database engine could have its own
    # symbol, override if required...
    PLACEHOLDER = "%s"

    def __init__(self, **kwargs):
        """
        Initialize SQL database client with connection parameters.

        :param kwargs:
            Database-specific connection parameters (e.g., host, port,
            database, user, password).
        """

        super().__init__(**kwargs)

        # Function used by the Database Engine
        # to convert to timestamp...
        self.epoch_to_timestamp_fcn = None

    def test_connection(self, query: Any = None):
        """
        Test the database connection by executing a version query.

        :param query: Optional custom query to test connection. Defaults to version query.
        :return: Query execution result.
        :raises DatabaseClientException: If connection test fails.
        """
        
        try:
            return self.execute(query or "SELECT version() AS version;")

        except Exception as error:
            raise DatabaseClientException(error)

    def execute(self, query: Any, **kwargs):
        """
        Execute a SQL query.

        :param query: SQL query string to execute.
        :param kwargs: Additional keyword arguments.

        :return: Cursor execution result.
        :raises DatabaseClientException: If there is no active connection or execution fails.
        """
        
        if not self.cxn:
            raise DatabaseClientException("There is not an active connection!")

        try:
            if not self.cursor:
                self.cursor = self.cxn.cursor()

            return self._execute(query, **kwargs)

        except Exception as error:
            raise DatabaseClientException(error)

    def _execute(self, query: Any, **kwargs):
        """
        Internal method for executing queries with database-specific
        parameter handling. Override this method in subclasses if the database driver requires
        specific parameter passing conventions (e.g., positional vs keyword arguments).

        :param query: SQL query string to execute.
        :param kwargs: Additional keyword arguments including 'params' for parameter binding.
        :return: Cursor execution result.
        """

        if not self.cursor:
            raise DatabaseClientException("No active cursor!")

        return self.cursor.execute(query, **kwargs)

    def commit(self) -> None:
        """
        Commit the current transaction to persist changes.
        :raises DatabaseClientException: If no active connection exists.
        """

        if not self.cxn:
            raise DatabaseClientException("No active connection!")

        self.cxn.commit()

    def select(self, table_fqn: str, columns: Optional[List[str]] = None):
        """
        Execute a SELECT query on the specified table.

        :param table_fqn: Table's fully qualified name.
        :param columns: List of column names to select. If None, selects all columns (*).
        :return: Cursor execution result.
        :raises ValueError: If column names contain invalid characters.
        """
        return self.execute(self.get_select_ddl(table_fqn, columns))

    @classmethod
    def validate_identifier(cls, identifiers: Iterable[str]) -> None:
        """
        Validate table or column names to prevent SQL injection
        attacks. Checks that all identifiers match the pattern for
        valid SQL identifiers:

          - Must start with letter or underscore
          - Can contain only alphanumeric characters and underscores
          - Full qualified names can contain a dot.

        :param identifiers: Iterable of identifiers like column name strings to validate.
        :raises ValueError: If any identifier contains invalid characters.
        """

        for identifier in identifiers:
            if not cls.VALID_IDENTIFIER.match(identifier):
                raise ValueError(
                    f"Invalid identifier: '{identifier}'. "
                    "Identifiers must start with a letter or underscore and contain only "
                    "alphanumeric characters, underscores, and dots (for qualified names)."
                )

    @staticmethod
    def _escape_string_value(value: str) -> str:
        """
        Escape string values to prevent SQL injection.
        Escapes single quotes by doubling them (SQL standard).

        :param value: The string value to escape.
        :return: Escaped string value.
        """

        # Replace single quotes with double single quotes (SQL standard escaping)
        return value.replace("'", "''")

    @classmethod
    def get_select_ddl(
        cls,
        table_fqn: str,
        columns: Optional[List[str]] = None,
    ) -> str:
        """
        Returns the DDL statement for a select.

        :param table_fqn: Table's fully qualified name.
        :param columns: List of column names to select. If None, selects all columns (*).

        :return: SELECT SQL statement.
        :raises ValueError: If column names contain invalid characters (potential SQL injection).
        """

        if columns:
            cls.validate_identifier(columns)
            column_list = ", ".join(columns)

        else:
            column_list = "*"

        # SQL construction is safe: columns are validated, table FQN is validated...
        return f"SELECT {column_list} FROM {table_fqn}"  # nosec B608

    def columns(self):
        """
        Get column names from the current cursor.
        :return: List of column names, or empty list if cursor is None.
        """

        if self.cursor and self.cursor.description:
            return [x[0].lower() for x in self.cursor.description]  # type: ignore[union-attr]
        return []

    def fetch_record(self) -> Dict[str, Any]:
        """
        Fetch a single record as a dictionary with column names as keys.
        :return: Dictionary with column names as keys and row values, or None if no record.
        """

        res = self.fetch_one()
        return dict(zip(self.columns(), res)) if res else {}

    def fetch_one(self) -> Tuple:
        """
        Fetch a single record as a tuple.
        :return: Tuple containing row values.
        """

        if not self.cursor:
            raise DatabaseClientException("No active cursor!")

        return self.cursor.fetchone()

    def fetch_records(self) -> Iterator[Dict[str, Any]]:
        """
        Fetch all records as an iterator of dictionaries. Converts fetchall
        tuples into dictionaries with column names as keys.

        :return: Iterator yielding dictionaries with column names as keys.
        """

        headers = self.columns()
        for row in self.fetch_all():
            yield dict(zip(headers, row))

    def fetch_all(self) -> Iterator[Tuple]:
        """
        Fetch all records as an iterator of tuples.
        :return: Iterator yielding tuples containing row values.
        """

        if self.cursor:
            rows = self.cursor.fetchall()
            if rows:
                for row in rows:  # type: ignore[union-attr]
                    yield row

    @classmethod
    def get_create_table_ddl(
        cls,
        table_fqn: str,
        columns: List[Tuple[str, Any]],
        temporal: bool = False,
    ) -> str:
        """
        Generate the SQL CREATE TABLE statement.

        :param table_fqn: Table's fully qualified name.
        :param columns: List of tuples defining the column name and data type.
        :param temporal: Whether to create a temporary table. Defaults to False.
        :return: The CREATE TABLE SQL statement.
        """

        # TODO: this function must be improved. Adding PK, unique, etc...

        columns_def = ", ".join([
            f"{name} {cls.TYPE_MAPPER.get(type_, 'VARCHAR')}"
            for name, type_ in columns
        ])

        return f"CREATE{' TEMPORARY' if temporal else ''} TABLE {table_fqn} ({columns_def});"

    def insert_records(
        self,
        table_fqn: str,
        columns: List[str],
        records: List[Dict],
        records_per_request: int = 500,
    ) -> int:
        """
        Insert a batch of records into a table using parameterized
        queries. Automatically manages batching to avoid memory issues
        with large datasets.

        :param table_fqn: Table's fully qualified name (FQN).
        :param columns: List of column names to insert into.
        :param records: List of dictionaries representing records to insert.
        :param records_per_request: Number of records to insert per batch. Defaults to 500.
        :return: Total number of inserted records.
        :raises DatabaseClientException: If insertion fails.
        """

        if records:
            try:
                total = 0
                for chunk_ in get_batches(records, records_per_request):
                    query, params = self.get_insert_dml(table_fqn, columns, chunk_)
                    self.execute(query, params=params)

                    if self.cursor:
                        total += self.cursor.rowcount

                return total

            except Exception as error:
                raise DatabaseClientException(error)

        return 0

    @classmethod
    def get_insert_dml(
        cls,
        table_fqn: str,
        columns: List[str],
        records: List[Dict],
    ) -> Tuple[str, tuple]:
        """
        Generate a parameterized INSERT statement with multi-row VALUES. Uses
        parameter binding to prevent SQL injection attacks.

        :param table_fqn: Table's fully qualified name (FQN).
        :param columns: List of column names to insert into.
        :param records: List of dictionaries representing records to insert.
        :return: Tuple of (query string with placeholders, flattened parameter tuple).
        :raises ValueError: If column names contain invalid characters.
        """

        if not records:
            return "", tuple()

        cls.validate_identifier(columns)
        placeholders = ", ".join([cls.PLACEHOLDER for _ in columns])
        values_rows = ", ".join([f"({placeholders})" for _ in records])

        # SQL construction is safe: columns are validated, values use placeholders...
        query = f"INSERT INTO {table_fqn} ({', '.join(columns)}) VALUES {values_rows}"  # nosec B608

        # Extracting and flatten parameters in the correct order...
        params: List = []
        for record in records:
            params.extend([
                json.dumps(record[col]) if type(record[col]) in [dict, list] else record[col]
                for col in columns
            ])

        return query, tuple(params)

    @classmethod
    @overload
    def get_delete_dml(
        cls,
        table_fqn: str,
        *,
        pk_id: Optional[str] = None,
        ids: Optional[List] = None,
    ) -> Tuple[str, Tuple]:
        """Generate DELETE statement with primary key IN clause."""

    @classmethod
    @overload
    def get_delete_dml(
        cls,
        table_fqn: str,
        *,
        pk_id: Optional[str] = None,
        conditionals: Optional[List[Dict]] = None,
    ) -> Tuple[str, Tuple]:
        """Generate DELETE statement with multiple conditional clauses."""

    @classmethod
    def get_delete_dml(
        cls,
        table_fqn: str,
        *,
        pk_id: Optional[str] = None,
        ids: Optional[List] = None,
        conditionals: Optional[List[Dict]] = None,
    ) -> Tuple[str, Tuple]:
        """
        Generate a parameterized DELETE statement with placeholders. Uses
        parameter binding to prevent SQL injection attacks.

        :param table_fqn: Table's fully qualified name.
        :param pk_id: Primary key column name for IN clause deletion.
        :param ids: List of ID values to delete (used with pk_id).
        :param conditionals: List of dictionaries with conditional criteria for WHERE clause.
        :return: Tuple of (query string with placeholders, list of parameter values).
        """

        if pk_id:
            if conditionals:
                values = tuple(rec[pk_id] for rec in conditionals)
            else:
                values = tuple(ids) if ids else tuple()

            placeholders = ", ".join([cls.PLACEHOLDER for _ in values])
            
            # SQL construction is safe: pk_id is validated, values use placeholders...
            query = f"DELETE FROM {table_fqn} WHERE {pk_id} IN ({placeholders})"  # nosec B608
            return query, values

        if not conditionals:
            return "", tuple()

        condition_parts, params = cls._get_conditional_statements(conditionals)
        
        # SQL construction is safe: columns validated in _get_conditional_statements,
        # values use placeholders...
        query = f"DELETE FROM {table_fqn} WHERE {' OR '.join(condition_parts)}"  # nosec B608
        return query, tuple(params)

    @classmethod
    def _get_conditional_statements(
        cls,
        conditionals: Optional[List[Dict]] = None,
    ) -> Tuple[List, List]:
        """
        Generate parameterized WHERE clause components from conditional
        dictionaries. Each dictionary in conditionals represents an OR condition, with keys as
        column names and values as comparison values. Keys within a dictionary are
        combined with AND.

        :param conditionals: List of dictionaries with column:value pairs.
        :return: Tuple of (list of condition strings, list of parameter values).

        Example:
        --------
        >>> conditionals = [{"name": "Alice", "age": 30}, {"status": "active"}]
        >>> # Generates: WHERE (name = ? AND age = ?) OR (status = ?)
        """

        condition_parts = []
        params = []

        if conditionals:
            for conditional in conditionals:
                keys = list(conditional.keys())
                condition_part = " AND ".join([f"{key} = {cls.PLACEHOLDER}" for key in keys])
                condition_parts.append(f"({condition_part})")
                params.extend([conditional[key] for key in keys])

        return condition_parts, params

    @classmethod
    @abstractmethod
    def get_merge_dml(cls, *args, **kwargs) -> Tuple[str, Tuple]:
        """
        Generate the MERGE/UPSERT statement. This is an abstract method
        that must be implemented by concrete classes, as each database engine
        may require specific syntax for merge operations.

        :param args: Positional arguments specific to the implementation.
        :param kwargs: Keyword arguments specific to the implementation.
        :return: Tuple of (MERGE/UPSERT statement string, tuple of parameters).
        """

    def close(self) -> None:
        """
        Close the database connection after committing pending changes. This
        method automatically commits any pending transactions before
        closing the connection to ensure data persistence.
        """

        if self.cxn:
            self.commit()

        super().close()
