# -*- coding: utf-8 -*-

"""
Database Engine Clients Module
================================

This module provides database client implementations for various
database systems. Each client implements the appropriate interface (IDatabaseClient
or ISqlDatabaseClient) and provides database-specific connection
handling, query execution, and data manipulation.

Available Database Clients:
---------------------------
  - **Db2Client**: IBM DB2 database client.
  - **MsSqlClient**: Microsoft SQL Server database client.
  - **MySQLClient**: MySQL database client.
  - **PostgresClient**: PostgreSQL database client.
  - **OracleClient**: Oracle Database client.
  - **SnowflakeClient**: Snowflake Data Warehouse client.
  - **MongoClient**: MongoDB NoSQL database client.

Usage:
------
.. code-block:: python

    from core_db.engines.postgres import PostgresClient

    with PostgresClient(conninfo="postgresql://user:pass@localhost/db") as client:
        client.execute("SELECT * FROM users;")
        for record in client.fetch_records():
            print(record)

Security:
---------
All SQL-based clients support parameterized queries to prevent SQL injection attacks.
Always use parameter binding for user-supplied values.

See individual client documentation for specific usage examples and connection parameters.
"""
