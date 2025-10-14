# -*- coding: utf-8 -*-

"""
IBM DB2 Database Client Module
================================

This module provides the Db2Client class for connecting to and interacting
with IBM DB2 databases using the ibm_db library.
"""

import json
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

import ibm_db

from core_db.interfaces.base import DatabaseClientException
from core_db.interfaces.sql_based import ISqlDatabaseClient


class Db2Client(ISqlDatabaseClient):
    """
    Client for IBM DB2 database connection...

    ===================================================
    How to use
    ===================================================

    .. code-block:: python

        from core_db.engines.db2 import Db2Client

        dsn_hostname, dsn_port, dsn_database = "localhost", "50000", "sample"
        dsn_uid, dsn_pwd = "db2inst1", "SomePassword"

        dsn = (
            f"DATABASE={dsn_database};"
            f"HOSTNAME={dsn_hostname};"
            f"PORT={dsn_port};"
            f"PROTOCOL=TCPIP;"
            f"UID={dsn_uid};"
            f"PWD={dsn_pwd};")

        with Db2Client(dsn=dsn, user="", password="") as client:
            client.execute("select * from department FETCH FIRST 2 ROWS ONLY;")
            print(client.fetch_one())
            print(client.fetch_record())
    ..
    """

    PLACEHOLDER = "?"

    def __init__(
        self,
        dsn: str,
        user: str = "",
        password: str = "",
        **kwargs,
    ) -> None:  # nosec B107
        super().__init__(dsn=dsn, user=user, password=password, **kwargs)
        self.connect_fcn = ibm_db.connect
        self.statement: Any = None

    @property
    def cursor(self):
        """
        IBM DB2 uses 'statement' instead of 'cursor'.
        This property provides compatibility with the base class.
        Returns a wrapper object that mimics cursor behavior.
        """

        class StatementWrapper:
            def __init__(self, statement):
                self._statement = statement

            @property
            def rowcount(self):
                if self._statement:
                    return ibm_db.num_rows(self._statement)
                return 0

        return StatementWrapper(self.statement)

    @cursor.setter
    def cursor(self, value):
        """
        Setter for cursor property to satisfy base class initialization.
        IBM DB2 doesn't use cursor, so this is a no-op.
        """

    def connect(self) -> None:
        """
        Establish connection to IBM DB2 database. Uses the DSN (Data Source Name) string
        along with user credentials to create a database connection
        using ibm_db.connect().

        :raises DatabaseClientException: If connection fails.
        """

        if not self.connect_fcn:
            raise DatabaseClientException("Connection function not set")

        try:
            self.cxn = self.connect_fcn(
                self.cxn_parameters.get("dsn", ""),
                self.cxn_parameters.get("user", ""),
                self.cxn_parameters.get("password", ""),
            )

        except Exception as error:
            raise DatabaseClientException(error) from error

    def test_connection(self, query: Optional[str] = None) -> Any:
        """
        Test the database connection by executing a simple query.

        :param query: Optional custom query to test. Defaults to querying DB2 system information.
        :return: Result of the query execution.
        """

        if not query:
            query = "SELECT * FROM SYSIBMADM.ENV_SYS_INFO FETCH FIRST 2 ROWS ONLY;"
        return self.execute(query)

    def execute(self, query: str, **kwargs) -> Any:
        """
        Execute SQL query with optional parameter binding. Uses `ibm_db.prepare`
        and `ibm_db.execute` for parameterized queries with parameter binding. For
        queries without parameters, uses ibm_db.exec_immediate
        for direct execution.

        :param query: SQL query string to execute.
        :param kwargs: Optional keyword arguments. Supports 'params' for parameter binding.
        :raises DatabaseClientException: If no connection exists or query execution fails.
        """

        if not self.cxn:
            raise DatabaseClientException("No active connection")

        params = kwargs.get("params", None)
        if params:
            # Use prepared statement with parameter binding
            self.statement = ibm_db.prepare(self.cxn, query)
            if not ibm_db.execute(self.statement, params):
                raise DatabaseClientException(f"Failed to execute query: {ibm_db.stmt_error()}")

        else:
            # Use immediate execution for non-parameterized queries
            self.statement = ibm_db.exec_immediate(self.cxn, query)

    def commit(self) -> None:
        """
        Commit the current transaction.
        :raises DatabaseClientException: If no active connection exists.
        """

        if not self.cxn:
            raise DatabaseClientException("No active connection")

        ibm_db.commit(self.cxn)

    def fetch_record(self) -> Dict[str, Any]:
        """
        Fetch the next row as a dictionary with column names as keys.
        :return: Dictionary representing a single row, or empty dict if no more rows.
        """

        result = ibm_db.fetch_assoc(self.statement)
        return result if result else {}  # type: ignore[return-value]

    def fetch_one(self) -> Tuple:
        """
        Fetch the next row as a tuple.
        :return: Tuple representing a single row.
        """
        return ibm_db.fetch_tuple(self.statement)

    def fetch_records(self) -> Iterator[Dict[str, Any]]:
        """
        Fetch all remaining rows as an iterator of dictionaries.
        :return: Iterator yielding dictionaries with column names as keys.
        """

        while row_ := ibm_db.fetch_assoc(self.statement):
            if isinstance(row_, dict):  # Type guard to ensure row_ is dict, not bool
                yield row_

    def fetch_all(self) -> Iterator[Tuple]:
        """
        Fetch all remaining rows as an iterator of tuples.
        :return: Iterator yielding tuples representing rows.
        """

        while row_ := ibm_db.fetch_tuple(self.statement):
            yield row_

    @classmethod
    def get_merge_dml(
        cls,
        table_fqn: str,
        pk_ids: List[str],
        columns: List[str],
        records: List[Dict],
    ) -> Tuple[str, Tuple]:
        """
        Generate parameterized MERGE statement for IBM DB2. Uses parameter
        binding to prevent SQL injection attacks.

        :param table_fqn: Table's fully qualified name.
        :param pk_ids: List of primary key column names.
        :param columns: List of column names.
        :param records: List of dictionaries representing records.

        :return: Tuple of (query string with placeholders, tuple of parameter values).
        :raises ValueError: If column names contain invalid characters.
        """

        if not records:
            return "", tuple()

        cls.validate_identifier(columns + pk_ids)

        # Create VALUES clause with ? placeholders
        placeholders = ", ".join(["?" for _ in columns])
        values_rows = ", ".join([f"({placeholders})" for _ in records])

        # Create source columns list
        source_columns = ", ".join(columns)

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
            USING (VALUES {values_rows}) AS source ({source_columns})
            ON ({on_conditions})
            WHEN MATCHED THEN
                UPDATE SET {set_statement}
            WHEN NOT MATCHED THEN
                INSERT ({insert_columns})
                VALUES ({insert_values})"""  # nosec B608

        # Extracting parameters in the correct order for each record
        params: List = []
        for record in records:
            params.extend([
                json.dumps(record[col]) if type(record[col]) in [dict, list] else record[col]
                for col in columns
            ])

        return query, tuple(params)

    def close(self):
        """
        Close the database connection. Safely closes the connection
        if one exists.
        """

        if self.cxn:
            ibm_db.close(self.cxn)
