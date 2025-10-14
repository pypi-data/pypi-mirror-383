# -*- coding: utf-8 -*-

"""
MongoDB Database Client Module
================================

This module provides the MongoClient class for connecting to and interacting
with MongoDB databases using the pymongo library.
"""

from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Optional

from pymongo import MongoClient as PyMongoClient
from pymongo.client_session import ClientSession
from pymongo.collation import Collation
from pymongo.results import DeleteResult
from pymongo.results import InsertManyResult
from pymongo.results import InsertOneResult

from core_db.interfaces.base import DatabaseClientException
from core_db.interfaces.base import IDatabaseClient


class MongoClient(IDatabaseClient):
    """
    Client for MongoDB connection...

    ===================================================
    How to use
    ===================================================

    .. code-block:: python

        from core_db.engines.mongo import MongoClient

        client = MongoClient(host="host", database="db")
        client.connect()
        print(client.test_connection())
    ..
    """

    def __init__(self, **kwargs):
        """
        Initialize MongoDB client.

        :param kwargs:
            Connection parameters. Must include 'database' parameter.
            Optional: host, port, username, password, and
            other MongoDB connection options.

        More information:
          - https://pymongo.readthedocs.io/en/stable/
          - https://www.mongodb.com/docs/manual/reference/connection-string/
        """

        self.db_name = kwargs.pop("database", None)
        super().__init__(**kwargs)
        self.connect_fcn = PyMongoClient
        self.db: Any = None

    def connect(self) -> None:
        """
        Establish connection to MongoDB database. Creates a connection
        using `PyMongoClient` and selects the specified database.

        :raises DatabaseClientException: If connection fails or database name is not provided.
        """

        super().connect()

        if not self.cxn:
            raise DatabaseClientException("Failed to establish connection")

        if not self.db_name:
            raise DatabaseClientException("Database name is required")

        self.db = self.cxn[self.db_name]

    def test_connection(
        self,
        query: Optional[str] = None,
        session: Optional[ClientSession] = None,
    ):
        """
        Test the database connection by retrieving server
        information. Executes MongoDB's `server_info()` command to
        verify connectivity and retrieve server metadata
        including version and configuration.

        :param query: Unused parameter (kept for interface compatibility).
        :param session: Optional ClientSession for the operation.
        :return: Dictionary containing MongoDB server information.
        :raises DatabaseClientException: If no active connection exists.
        """

        if not self.cxn:
            raise DatabaseClientException("No active connection")
        return self.cxn.server_info(session=session)

    def find_one(
        self,
        collection_name: str,
        filters: Optional[Dict] = None,
        projection: Optional[Dict] = None,
        *args,
        **kwargs,
    ) -> Dict:
        """
        Get a single document from the database. All arguments to find() are also
        valid arguments for find_one(), although any limit argument will be ignored. Returns
        a single document, or None if no matching document is found.

        :param collection_name: The collection to which you want to add documents.

        :param filters:
            A dictionary specifying the query to be performed OR any other
            type to be used as the value for a query for "_id".

        :param projection:
            A list of field names that should be returned in the result set or
            a dict specifying the fields to include or exclude. If projection is
            a list “_id” will always be returned. Use a dict to exclude fields
            from the result (e.g. projection={‘_id’: False}).

        args: Any additional positional arguments are the same as the arguments to find().
        kwargs: Any additional keyword arguments are the same as the arguments to find().
        """

        if not filters:
            filters = {}

        if not projection:
            projection = {}

        return getattr(self.db, collection_name).find_one(filters, projection, *args, **kwargs)

    def find(
        self,
        collection_name: str,
        filters: Optional[Dict] = None,
        projection: Optional[Dict] = None,
        *args,
        **kwargs,
    ) -> Iterator:
        """
        Query the database. The filters argument is a query document
        that all results must match...

        https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.find

        :param collection_name: The collection to which you want to add documents.

        :param filters:
            A dictionary specifying the query to be performed OR any other
            type to be used as the value for a query for "_id".

        :param projection:
            A list of field names that should be returned in the result set or
            a dict specifying the fields to include or exclude. If projection is
            a list “_id” will always be returned. Use a dict to exclude fields
            from the result (e.g. projection={‘_id’: False}).

        For args/kwargs you can check the documentation.
        """

        if not filters:
            filters = {}

        if not projection:
            projection = {}

        cursor = getattr(self.db, collection_name).find(filters, projection, *args, **kwargs)
        for record in cursor:
            yield record

    def insert_one(
        self,
        collection_name: str,
        document: Dict,
        bypass_document_validation: bool = False,
        session: Optional[ClientSession] = None,
        comment: Optional[str] = None,
    ) -> InsertOneResult:
        """
        This is a method by which we can insert a single entry within
        the collection or the database in MongoDB. If the collection does
        not exist this method creates a new collection and insert the
        data into it. It takes a dictionary as a parameter containing the
        name and value of each field in the document you want to insert
        in the collection.

        :param collection_name: The collection to which you want to add documents.

        :param document:
            The document to insert. Must be a mutable mapping type. If the
            document does not have an _id field one will be added automatically.

        :param bypass_document_validation:
            If “True”, allows the write to opt-out of document level
            validation. Default is “False”.

        :param session: A class ‘~pymongo.client_session.ClientSession’.
        :param comment: A user-provided comment to attach to this command.

        """

        return getattr(
            self.db,
            collection_name,
        ).insert_one(
            document,
            session=session,
            bypass_document_validation=bypass_document_validation,
            comment=comment,
        )

    def insert_many(
        self,
        collection_name: str,
        documents: List[Dict],
        ordered: bool = True,
        bypass_document_validation: bool = False,
        session: Optional[ClientSession] = None,
    ) -> InsertManyResult:
        """
        This method is used to insert multiple entries in a collection or the
        database in MongoDB. The parameter of this method is a list that contains
        dictionaries of the data that we want to insert in the collection.

        This method returns an instance of class “~pymongo.results.InsertManyResult” which
        has a “_id” field that holds the id of the inserted documents. If the document does not
        specify an “_id” field, then MongoDB will add the “_id” field to all the data in the
        list and assign a unique object id for the documents before inserting.

        :param collection_name: The collection to which you want to add documents.
        :param documents: A iterable of documents to insert.

        :param ordered:
            If “True” (the default) documents will be inserted on
            the server serially, in the order provided. If an error
            occurs all remaining inserts are aborted. If “False”, documents
            will be inserted on the server in arbitrary order, possibly
            in parallel, and all document inserts will be attempted.

        :param bypass_document_validation:
            If “True”, allows the write to opt-out of document level
            validation. Default is “False”.

        :param session: A class ‘~pymongo.client_session.ClientSession’.
        """

        return getattr(
            self.db,
            collection_name,
        ).insert_many(
            documents,
            ordered=ordered,
            bypass_document_validation=bypass_document_validation,
            session=session,
        )

    def delete_one(
        self,
        collection_name: str,
        filter_query: Dict,
        collation: Optional[Collation] = None,
        hint=None,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
    ) -> DeleteResult:
        """
        To remove one document from the collection...

        :param collection_name: The collection to which you want to add documents.
        :param filter_query: A query that matches the document to delete.

        :param collation:
            An instance of class: ‘~pymongo.collation.Collation’. This option
            is only supported on MongoDB 3.4 and above.

        :param hint:
            An index to use to support the query predicate. This option
            is only supported on MongoDB 3.11 and above.

        :param session: A class ‘~pymongo.client_session.ClientSession’.

        :param let:
            Map of parameter names and values. Values must be constant or closed
            expressions that do not reference document fields. Parameters can then be
            accessed as variables in an aggregate expression context (e.g. "$$var").

        :param comment: A user-provided comment to attach to this command.
        """

        return getattr(
            self.db,
            collection_name,
        ).delete_one(
            filter_query,
            collation=collation,
            hint=hint,
            session=session,
            let=let,
            comment=comment,
        )

    def delete_many(
        self,
        collection_name: str,
        filter_query: Dict,
        collation: Optional[Collation] = None,
        hint=None,
        session: Optional[ClientSession] = None,
        let: Optional[Mapping[str, Any]] = None,
        comment: Optional[Any] = None,
    ) -> DeleteResult:
        """
        It is used when one needs to delete more than one document. A query
        object containing which document to be deleted is created and is passed
        as the first parameter to the delete_many().

        :param collection_name: The collection to which you want to add documents.
        :param filter_query: A query that matches the document to delete.

        :param collation:
            An instance of class: ‘~pymongo.collation.Collation’. This option
            is only supported on MongoDB 3.4 and above.

        :param hint:
            An index to use to support the query predicate. This option
            is only supported on MongoDB 3.11 and above.

        :param session: A class ‘~pymongo.client_session.ClientSession’.

        :param let:
            Map of parameter names and values. Values must be constant or closed
            expressions that do not reference document fields. Parameters can then be
            accessed as variables in an aggregate expression context (e.g. "$$var").

        :param comment: A user-provided comment to attach to this command.
        """

        return getattr(self.db, collection_name).delete_many(
            filter_query,
            collation=collation,
            hint=hint,
            session=session,
            let=let,
            comment=comment,
        )
