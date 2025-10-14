# -*- coding: utf-8 -*-

"""
ETL (Extract, Transform, Load) Base Classes Module
===================================================

This module provides abstract base classes for building ETL processes that
retrieve data from database sources. These classes integrate with the `core_etl`
framework to provide record-based processing capabilities.


Available Classes:
------------------
  - **IBaseEtlFromDatabase**: Abstract base class for ETL processes that extract
    data from databases and process records in batches.


Usage:
------
.. code-block:: python

    from core_db.etls.database_based import IBaseEtlFromDatabase

    class MyDatabaseETL(IBaseEtlFromDatabase):
        def _execute_query(self, query):
            self.db_client.execute(query)

        def _fetch_records(self):
            return self.db_client.fetch_records()

        def process_records(self, records, **kwargs):
            # Process the records
            pass
..

See individual class documentation for specific usage examples
and implementation details.
"""

from .database_based import IBaseEtlFromDatabase


__all__ = [
    "IBaseEtlFromDatabase",
]
