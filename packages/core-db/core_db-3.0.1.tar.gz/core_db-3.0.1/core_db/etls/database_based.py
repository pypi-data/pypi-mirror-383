# -*- coding: utf-8 -*-

"""
Database-Based ETL Module
==========================

This module provides abstract base classes for building ETL (Extract, Transform, Load)
processes that extract data from database sources. It extends the core_etl framework
to provide specialized database connectivity and query execution capabilities.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

from core_etl.record_based import IBaseEtlFromRecord

from core_db.interfaces.base import IDatabaseClient


class IBaseEtlFromDatabase(IBaseEtlFromRecord, ABC):
    """
    Abstract base class for ETL processes that extract data from
    databases. This class extends IBaseEtlFromRecord to provide specialized
    functionality for retrieving data from database sources. It manages
    database connections, executes queries, and processes records
    in configurable batches.

    The class handles the complete lifecycle of database-based ETL operations:
      - Connection establishment in pre_processing.
      - Query execution and data retrieval.
      - Batch-based record processing.
      - Connection cleanup in clean_resources.

    Attributes:
        database_type (str): The class name of the database client to use.
        connection_parameters (Dict): Parameters for establishing database connection.
        db_client (Optional[IDatabaseClient]): Active database client instance.
        base_query (Optional[str]): Base SQL query template for data retrieval.

    Usage:
    ------

    .. code-block:: python

        class MyETL(IBaseEtlFromDatabase):
            def _execute_query(self, query):
                self.db_client.execute(query)

            def _fetch_records(self):
                return self.db_client.fetch_records()

            def process_records(self, records, **kwargs):
                # Transform and load records
                for record in records:
                    self.transform_and_load(record)

        # Execute the ETL
        etl = MyETL(
            database_type="PostgresClient",
            connection_parameters={"conninfo": "postgresql://..."},
            base_query="SELECT * FROM source_table",
            max_per_batch=1000
        )
        etl.run()
    ..
    """

    def __init__(
        self,
        database_type: str,
        connection_parameters: Dict,
        base_query: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        :param database_type: The name of the class that defines the database connection.
        :param connection_parameters: The parameters to create the database connection.
        :param base_query: Query base to use when retrieving data.
        """

        super().__init__(**kwargs)

        self.database_type = database_type
        self.connection_parameters = connection_parameters
        self.db_client: Optional[IDatabaseClient] = None
        self.base_query = base_query

    def pre_processing(self, **kwargs) -> None:
        """
        Initialize database connection before ETL processing begins. This
        method is called automatically before the ETL
        process starts. It:

          1. Retrieves the appropriate database client class using the factory pattern
          2. Instantiates the client with provided connection parameters
          3. Establishes the database connection

        :param kwargs: Additional keyword arguments passed to parent pre_processing.
        :raises DatabaseClientException: If connection fails or database_type is invalid.
        """
        
        super().pre_processing(**kwargs)

        database_cls = IDatabaseClient.get_class(self.database_type)
        self.db_client = database_cls(**self.connection_parameters) if database_cls else None
        if self.db_client:
            self.db_client.connect()

    def get_query(self, *args, **kwargs) -> Optional[str]:
        """
        Generate or return the SQL query for data retrieval. Override this
        method to implement dynamic query generation based on ETL parameters
        like date ranges, last processed values, or other criteria.

        :param args: Positional arguments for query generation.
        :param kwargs: Keyword arguments (last_processed, start, end, etc.).
        :return: SQL query string, or None if no query is needed.
        """
        return self.base_query

    def retrieve_records(
        self,
        last_processed: Any = None,
        start: Any = None,
        end: Any = None,
        **kwargs,
    ) -> Iterator[List[Dict]]:
        """
        Retrieve records from the database in batches. This method
        orchestrates the data retrieval process by:

          1. Generating the appropriate query using get_query().
          2. Executing the query via _execute_query().
          3. Fetching records via _fetch_records().
          4. Batching records according to max_per_batch.
          5. Yielding batches for processing.

        :param last_processed: Identifier of the last processed record for incremental loads.
        :param start: Start boundary for data extraction (timestamp, ID, etc.).
        :param end: End boundary for data extraction (timestamp, ID, etc.).
        :param kwargs: Additional query parameters.
        :yield: Batches of records as lists of dictionaries.
        """

        if self.db_client:
            self._execute_query(
                self.get_query(
                    last_processed=last_processed,
                    start=start, end=end,
                    **kwargs
                )
            )

            batch = []
            for record in self._fetch_records():
                batch.append(record)
                if len(batch) == self.max_per_batch:
                    yield batch
                    batch = []

            # Yielding any remaining records that
            # didn't reach max_per_batch...
            if batch:
                yield batch

    @abstractmethod
    def _execute_query(self, query: Any):
        """
        Execute the SQL query on the database connection. Concrete
        implementations must define this method to handle database-specific
        query execution. This typically involves calling the appropriate
        method on self.db_client.

        :param query: SQL query string to execute.
        """

    @abstractmethod
    def _fetch_records(self) -> Iterator[Dict]:
        """
        Fetch records from the executed query result. Concrete
        implementations must define this method to retrieve records
        from the database cursor or result set. This typically
        returns an iterator from the database client.

        :return: Iterator yielding dictionaries with column names as keys.
        """

    def process_records(self, records: List[Dict], **kwargs):
        """
        Process a batch of transformed records. Concrete implementations
        must define the load operations to perform with the
        transformed records. Common actions include:

          - Loading to target database.
          - Archiving to S3 or cloud storage.
          - Sending to message queues (SQS, Kinesis, Kafka).
          - Writing to files or SFTP servers.
          - Sending to APIs or webhooks.

        :param records: List of dictionaries representing processed records.
        :param kwargs: Additional parameters for processing.
        """

    def clean_resources(self) -> None:
        """
        Clean up database connection and resources after ETL
        completion. This method is called automatically at the end of the ETL process
        to ensure proper cleanup. It safely closes the database connection
        if one exists.
        """

        if self.db_client:
            if getattr(self.db_client, "close", False):
                self.db_client.close()
