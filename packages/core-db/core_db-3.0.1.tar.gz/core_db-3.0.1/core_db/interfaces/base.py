# -*- coding: utf-8 -*-

"""
This module provides abstract base classes and exceptions for
implementing database clients with a standardized interface across
different database engines.
"""

from abc import ABC, abstractmethod
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional

from core_mixins import Self
from core_mixins.interfaces.factory import IFactory


class IDatabaseClient(IFactory, ABC):
    """
    Abstract base class for all database clients.

    This class provides a standardized interface for connecting to and interacting
    with various database engines. It implements the context manager protocol for
    automatic resource management and integrates with the factory pattern for
    dynamic client instantiation.

    Attributes:
        TYPE_MAPPER (Dict[Any, str]): Mapping from Python types to database-specific
            type names. Should be overridden by subclasses to provide engine-specific
            type conversions.

        cxn_parameters (dict): Connection parameters passed during initialization.
        cursor: Database cursor object for executing queries.
        cxn: Active database connection object.
        connect_fcn: Function used to establish connection to the database engine.
    """

    # Mapper for python types to database types...
    TYPE_MAPPER: Dict[Any, str] = {}

    def __init__(self, **kwargs) -> None:
        """
        Initialize the database client with connection parameters.

        :param **kwargs:
            Arbitrary keyword arguments representing database-specific
            connection parameters (e.g., host, port, database,
            user, password).
        """

        self.cxn_parameters = kwargs
        self.cursor = None
        self.cxn = None

        # Function used by the library to perform
        # the connection to the engine...
        self.connect_fcn: Optional[Callable[..., Any]] = None

    def __enter__(self) -> Self:
        """
        Enter the runtime context for the database client. Establishes
        the database connection when entering a 'with' block.

        :returns: The database client instance.
        """

        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context for the database client. Commits pending
        changes and closes the connection when exiting a 'with' block.

        :param exc_type: Exception type if an exception was raised.
        :param exc_val: Exception value if an exception was raised.
        :param exc_tb: Exception traceback if an exception was raised.
        """

        self.close()

    @classmethod
    def registration_key(cls) -> str:
        """
        Get the registration key for the factory pattern.
        :returns: The class name used as the registration key.
        """

        return cls.__name__

    def connect(self) -> None:
        """
        Establish a connection to the database. Uses the connection
        function and parameters provided during initialization
        to create a connection to the database engine.

        :raises:
            DatabaseClientException: If the connection fails for any reason.
        """

        try:
            if not self.connect_fcn:
                raise DatabaseClientException("Connection function not set")
            self.cxn = self.connect_fcn(**self.cxn_parameters)

        except Exception as error:
            raise DatabaseClientException(error)

    @abstractmethod
    def test_connection(self, query: Any):
        """
        Test the database connection by executing a simple query.

        :param query (Any):
            A simple test query to verify the connection is working
            (e.g., "SELECT 1" for most databases).
        """

    def close(self) -> None:
        """
        Close the database connection and release resources. This
        method safely closes the connection if one exists, releasing any
        database resources held by the client.
        """

        if self.cxn:
            if getattr(self.cxn, "close", False):
                self.cxn.close()


class DatabaseClientException(Exception):
    """
    Custom exception for database client operations. Raised when
    a database operations fail, including connection errors, query
    execution errors, or other database-related issues.
    """
