from __future__ import annotations
from ..bulk_operations import BulkOperationExecutor
from ..exceptions import MalformedQueryException
from ..requests import DeleteOne, InsertOne, UpdateOne
from ..results import (
    BulkWriteResult,
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)
from .cursor import Cursor, DESCENDING
from .query_helper import QueryHelper
from .raw_batch_cursor import RawBatchCursor
from .sql_translator_unified import SQLTranslator
from copy import deepcopy
from neosqlite.collection.json_helpers import (
    neosqlite_json_dumps,
    neosqlite_json_loads,
)
from neosqlite.collection.jsonb_support import supports_jsonb
from typing import Any, Dict, List, TYPE_CHECKING
import importlib.util
import json

if TYPE_CHECKING:
    from quez import CompressedQueue

# Check if quez is available
_HAS_QUEZ = importlib.util.find_spec("quez") is not None


class QueryEngine:
    """
    A class that provides methods for querying and manipulating documents in a collection.

    The QueryEngine handles all database operations including inserting, updating, deleting,
    and finding documents. It also supports aggregation pipelines, bulk operations, and
    various utility methods for counting and retrieving distinct values.
    """

    def __init__(self, collection):
        """
        Initialize the QueryEngine with a collection.

        Args:
            collection: The collection instance this QueryEngine will operate on.
        """
        self.collection = collection
        self.helpers = QueryHelper(collection)
        # Check if JSONB is supported for this connection
        self._jsonb_supported = supports_jsonb(collection.db)
        self.sql_translator = SQLTranslator(
            collection.name, "data", "id", self._jsonb_supported
        )

    def insert_one(self, document: Dict[str, Any]) -> InsertOneResult:
        """
        Insert a single document into the collection.

        Args:
            document (Dict[str, Any]): The document to insert.

        Returns:
            InsertOneResult: The result of the insert operation, containing the inserted document ID.
        """
        inserted_id = self.helpers._internal_insert(document)
        return InsertOneResult(inserted_id)

    def insert_many(self, documents: List[Dict[str, Any]]) -> InsertManyResult:
        """
        Insert multiple documents into the collection.

        Args:
            documents (List[Dict[str, Any]]): List of documents to insert.

        Returns:
            InsertManyResult: Result of the insert operation, containing a list of inserted document IDs.
        """
        inserted_ids = [self.helpers._internal_insert(doc) for doc in documents]
        return InsertManyResult(inserted_ids)

    def update_one(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> UpdateResult:
        """
        Updates a single document in the collection based on the provided filter
        and update operations.

        Args:
            filter (Dict[str, Any]): A dictionary specifying the query criteria for finding the document to update.
            update (Dict[str, Any]): A dictionary specifying the update operations to apply to the document.
            upsert (bool, optional): If True, inserts a new document if no document matches the filter. Defaults to False.

        Returns:
            UpdateResult: An object containing information about the update operation,
                          including the count of matched and modified documents,
                          and the upserted ID if applicable.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        filter = self.helpers._normalize_id_query(filter)
        # Find the document using the filter, but we need to work with integer IDs internally
        # For internal operations, we need to retrieve the document differently to get the integer id
        # We'll use a direct SQL query to get both the integer id and the stored _id
        where_clause, params = self.sql_translator.translate_match(filter)
        if where_clause:
            # Get the integer id as well for internal operations
            # Use the same approach as the original code considering JSONB support
            if self.collection.query_engine._jsonb_supported:
                cmd = f"SELECT id, _id, json(data) as data FROM {self.collection.name} {where_clause} LIMIT 1"
            else:
                cmd = f"SELECT id, _id, data FROM {self.collection.name} {where_clause} LIMIT 1"
            cursor = self.collection.db.execute(cmd, params)
            row = cursor.fetchone()
            if row:
                int_id, stored_id, data = row
                # Load the document the normal way for the update processing
                doc = self.collection._load_with_stored_id(
                    int_id, data, stored_id
                )
                # Use the integer id for internal operations
                self.helpers._internal_update(int_id, update, doc)
                return UpdateResult(
                    matched_count=1, modified_count=1, upserted_id=None
                )
        else:
            # Fallback to find_one if translation doesn't work
            if doc := self.find_one(filter):
                # Get integer id by looking up the stored ObjectId
                int_doc_id = self._get_integer_id_for_oid(doc["_id"])
                self.helpers._internal_update(int_doc_id, update, doc)
                return UpdateResult(
                    matched_count=1, modified_count=1, upserted_id=None
                )

        if upsert:
            # For upsert, we need to create a document that includes:
            # 1. The filter fields (as base document)
            # 2. Apply the update operations to that document
            new_doc: Dict[str, Any] = dict(filter)  # Start with filter fields
            new_doc = self.helpers._internal_update(
                0, update, new_doc
            )  # Apply updates
            inserted_id = self.insert_one(new_doc).inserted_id
            return UpdateResult(
                matched_count=0, modified_count=0, upserted_id=inserted_id
            )

        return UpdateResult(matched_count=0, modified_count=0, upserted_id=None)

    def _get_integer_id_for_oid(self, oid) -> int:
        """
        Get the integer ID for a given ObjectId.

        Args:
            oid: The ObjectId to look up.

        Returns:
            int: The corresponding integer ID from the database.

        Raises:
            ValueError: If the integer ID for the ObjectId cannot be found.
        """
        # This method should find the integer id in the database that corresponds to the ObjectId
        cursor = self.collection.db.execute(
            f"SELECT id FROM {self.collection.name} WHERE _id = ?",
            (str(oid) if hasattr(oid, "__str__") else oid,),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        # If not found, it might be that the _id is not stored in the _id column
        # This could happen for older records
        if isinstance(oid, int):
            return oid
        raise ValueError(f"Could not find integer ID for ObjectId: {oid}")

    def update_many(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> UpdateResult:
        """
        Update multiple documents based on a filter.

        This method updates documents in the collection that match the given filter
        using the specified update.

        Args:
            filter (Dict[str, Any]): A dictionary representing the filter to select documents to update.
            update (Dict[str, Any]): A dictionary representing the updates to apply.

        Returns:
            UpdateResult: A result object containing information about the update operation.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        filter = self.helpers._normalize_id_query(filter)
        # Try to use SQLTranslator for the WHERE clause
        where_clause, where_params = self.sql_translator.translate_match(filter)

        # Get the update clause using existing helper
        update_result = self.helpers._build_update_clause(update)

        if where_clause is not None and update_result is not None:
            set_clause, set_params = update_result
            cmd = (
                f"UPDATE {self.collection.name} SET {set_clause} {where_clause}"
            )
            cursor = self.collection.db.execute(cmd, set_params + where_params)
            return UpdateResult(
                matched_count=cursor.rowcount,
                modified_count=cursor.rowcount,
                upserted_id=None,
            )

        # Fallback for complex queries
        # Get the integer IDs for the documents to update
        where_clause, where_params = self.sql_translator.translate_match(filter)
        if where_clause is not None:
            cmd = f"SELECT id FROM {self.collection.name} {where_clause}"
            cursor = self.collection.db.execute(cmd, where_params)
            ids = [row[0] for row in cursor.fetchall()]
        else:
            # If we can't translate the filter, we'll need to get all docs and filter in memory
            docs = list(self.find(filter))
            ids = []
            for doc in docs:
                int_doc_id = self._get_integer_id_for_oid(doc["_id"])
                ids.append(int_doc_id)

        modified_count = 0
        for int_doc_id in ids:
            # Get the document using the integer ID for the update
            if self.collection.query_engine._jsonb_supported:
                cmd = f"SELECT id, _id, json(data) as data FROM {self.collection.name} WHERE id = ?"
            else:
                cmd = f"SELECT id, _id, data FROM {self.collection.name} WHERE id = ?"
            cursor = self.collection.db.execute(cmd, (int_doc_id,))
            row = cursor.fetchone()
            if row:
                int_id, stored_id, data = row
                doc = self.collection._load_with_stored_id(
                    int_id, data, stored_id
                )
                self.helpers._internal_update(int_doc_id, update, doc)
                modified_count += 1
        return UpdateResult(
            matched_count=len(ids),
            modified_count=modified_count,
            upserted_id=None,
        )

    def delete_one(self, filter: Dict[str, Any]) -> DeleteResult:
        """
        Delete a single document matching the filter.

        Args:
            filter (Dict[str, Any]): A dictionary specifying the filter conditions
                                     for the document to delete.

        Returns:
            DeleteResult: A result object indicating whether the deletion was
                          successful or not.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        filter = self.helpers._normalize_id_query(filter)
        # Use direct query to get integer ID for the delete operation
        where_clause, params = self.sql_translator.translate_match(filter)
        if where_clause:
            cmd = (
                f"SELECT id FROM {self.collection.name} {where_clause} LIMIT 1"
            )
            cursor = self.collection.db.execute(cmd, params)
            row = cursor.fetchone()
            if row:
                int_id = row[0]
                self.helpers._internal_delete(int_id)
                return DeleteResult(deleted_count=1)
        else:
            # Fallback approach
            if doc := self.find_one(filter):
                int_doc_id = self._get_integer_id_for_oid(doc["_id"])
                self.helpers._internal_delete(int_doc_id)
                return DeleteResult(deleted_count=1)
        return DeleteResult(deleted_count=0)

    def delete_many(self, filter: Dict[str, Any]) -> DeleteResult:
        """
        Deletes multiple documents in the collection that match the provided filter.

        Args:
            filter (Dict[str, Any]): A dictionary specifying the query criteria
                                     for finding the documents to delete.

        Returns:
            DeleteResult: A result object indicating whether the deletion was successful or not.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        filter = self.helpers._normalize_id_query(filter)
        # Try to use SQLTranslator for the WHERE clause
        where_clause, params = self.sql_translator.translate_match(filter)
        if where_clause is not None:
            cmd = f"DELETE FROM {self.collection.name} {where_clause}"
            cursor = self.collection.db.execute(cmd, params)
            return DeleteResult(deleted_count=cursor.rowcount)

        # Fallback for complex queries
        # Get integer IDs for the documents to delete
        where_clause, params = self.sql_translator.translate_match(filter)
        if where_clause is not None:
            # Use direct SQL if possible
            cmd = f"SELECT id FROM {self.collection.name} {where_clause}"
            cursor = self.collection.db.execute(cmd, params)
            ids = [row[0] for row in cursor.fetchall()]
        else:
            # Fallback to finding documents and getting their integer IDs
            docs = list(self.find(filter))
            if not docs:
                return DeleteResult(deleted_count=0)
            ids = []
            for d in docs:
                int_doc_id = self._get_integer_id_for_oid(d["_id"])
                ids.append(int_doc_id)

        if not ids:
            return DeleteResult(deleted_count=0)

        placeholders = ",".join("?" for _ in ids)
        self.collection.db.execute(
            f"DELETE FROM {self.collection.name} WHERE id IN ({placeholders})",
            ids,
        )
        return DeleteResult(deleted_count=len(ids))

    def replace_one(
        self,
        filter: Dict[str, Any],
        replacement: Dict[str, Any],
        upsert: bool = False,
    ) -> UpdateResult:
        """
        Replace one document in the collection that matches the filter with the
        replacement document.

        Args:
            filter (Dict[str, Any]): A query that matches the document to replace.
            replacement (Dict[str, Any]): The new document that replaces the matched document.
            upsert (bool, optional): If true, inserts the replacement document if no document matches the filter.
                                     Default is False.

        Returns:
            UpdateResult: A result object containing the number of matched and
                          modified documents and the upserted ID.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        filter = self.helpers._normalize_id_query(filter)
        # Find the document using the filter, but get the integer ID for internal operations
        where_clause, params = self.sql_translator.translate_match(filter)
        if where_clause:
            if self.collection.query_engine._jsonb_supported:
                cmd = f"SELECT id, _id, json(data) as data FROM {self.collection.name} {where_clause} LIMIT 1"
            else:
                cmd = f"SELECT id, _id, data FROM {self.collection.name} {where_clause} LIMIT 1"
            cursor = self.collection.db.execute(cmd, params)
            row = cursor.fetchone()
            if row:
                int_id, stored_id, data = row
                self.helpers._internal_replace(int_id, replacement)
                return UpdateResult(
                    matched_count=1, modified_count=1, upserted_id=None
                )
        else:
            # Fallback approach
            if doc := self.find_one(filter):
                int_doc_id = self._get_integer_id_for_oid(doc["_id"])
                self.helpers._internal_replace(int_doc_id, replacement)
                return UpdateResult(
                    matched_count=1, modified_count=1, upserted_id=None
                )

        if upsert:
            inserted_id = self.insert_one(replacement).inserted_id
            return UpdateResult(
                matched_count=0, modified_count=0, upserted_id=inserted_id
            )

        return UpdateResult(matched_count=0, modified_count=0, upserted_id=None)

    def find(
        self,
        filter: Dict[str, Any] | None = None,
        projection: Dict[str, Any] | None = None,
        hint: str | None = None,
    ) -> Cursor:
        """
        Query the database and retrieve documents matching the provided filter.

        Args:
            filter (Dict[str, Any] | None): A dictionary specifying the query criteria.
            projection (Dict[str, Any] | None): A dictionary specifying which fields to return.
            hint (str | None): A string specifying the index to use.

        Returns:
            Cursor: A cursor object to iterate over the results.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        if filter is not None:
            filter = self.helpers._normalize_id_query(filter)
        return Cursor(self.collection, filter, projection, hint)

    def find_raw_batches(
        self,
        filter: Dict[str, Any] | None = None,
        projection: Dict[str, Any] | None = None,
        hint: str | None = None,
        batch_size: int = 100,
    ) -> RawBatchCursor:
        """
        Query the database and retrieve batches of raw JSON.

        Similar to the :meth:`find` method but returns a
        :class:`~neosqlite.raw_batch_cursor.RawBatchCursor`.

        This method returns raw JSON batches which can be more efficient for
        certain use cases where you want to process data in batches rather than
        individual documents.

        Args:
            filter (Dict[str, Any] | None): A dictionary specifying the query criteria.
            projection (Dict[str, Any] | None): A dictionary specifying which fields to return.
            hint (str | None): A string specifying the index to use.
            batch_size (int): The number of documents to include in each batch.

        Returns:
            RawBatchCursor instance.

        Example usage:

        >>> import json
        >>> cursor = collection.find_raw_batches()
        >>> for batch in cursor:
        ...     # Each batch is raw bytes containing JSON documents separated by newlines.
        ...     documents = [json.loads(doc) for doc in batch.decode('utf-8').split('\\n') if doc]
        ...     print(documents)
        """
        return RawBatchCursor(
            self.collection, filter, projection, hint, batch_size
        )

    def find_one(
        self,
        filter: Dict[str, Any] | None = None,
        projection: Dict[str, Any] | None = None,
        hint: str | None = None,
    ) -> Dict[str, Any] | None:
        """
        Find a single document matching the filter.

        Args:
            filter (Dict[str, Any]): A dictionary specifying the filter conditions.
            projection (Dict[str, Any]): A dictionary specifying which fields to return.
            hint (str): A string specifying the index to use (not used in SQLite).

        Returns:
            Dict[str, Any]: A dictionary representing the found document,
                            or None if no document matches.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        if filter is not None:
            filter = self.helpers._normalize_id_query(filter)
        try:
            return next(iter(self.find(filter, projection, hint).limit(1)))
        except StopIteration:
            return None

    def find_one_and_delete(
        self,
        filter: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        """
        Deletes a document that matches the filter and returns it.

        Args:
            filter (Dict[str, Any]): A dictionary specifying the filter criteria.

        Returns:
            Dict[str, Any] | None: The document that was deleted,
                                   or None if no document matches.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        filter = self.helpers._normalize_id_query(filter)
        # Find document and get its integer ID for the delete operation
        where_clause, params = self.sql_translator.translate_match(filter)
        if where_clause:
            if self.collection.query_engine._jsonb_supported:
                cmd = f"SELECT id, _id, json(data) as data FROM {self.collection.name} {where_clause} LIMIT 1"
            else:
                cmd = f"SELECT id, _id, data FROM {self.collection.name} {where_clause} LIMIT 1"
            cursor = self.collection.db.execute(cmd, params)
            row = cursor.fetchone()
            if row:
                int_id, stored_id, data = row
                doc = self.collection._load_with_stored_id(
                    int_id, data, stored_id
                )
                self.helpers._internal_delete(int_id)
                return doc
        else:
            # Fallback approach
            if doc := self.find_one(filter):
                int_doc_id = self._get_integer_id_for_oid(doc["_id"])
                self.helpers._internal_delete(int_doc_id)
                return doc
        return None

    def find_one_and_replace(
        self,
        filter: Dict[str, Any],
        replacement: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        """
        Replaces a single document in the collection based on a filter with a new document.

        This method first finds a document matching the filter, then replaces it
        with the new document. If the document is found and replaced, the original
        document is returned; otherwise, None is returned.

        Args:
            filter (Dict[str, Any]): A dictionary representing the filter to search for the document to replace.
            replacement (Dict[str, Any]): A dictionary representing the new document to replace the existing one.

        Returns:
            Dict[str, Any] | None: The original document that was replaced,
                                   or None if no document was found and replaced.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        filter = self.helpers._normalize_id_query(filter)
        # Find document and get its integer ID for the replace operation
        where_clause, params = self.sql_translator.translate_match(filter)
        if where_clause:
            if self.collection.query_engine._jsonb_supported:
                cmd = f"SELECT id, _id, json(data) as data FROM {self.collection.name} {where_clause} LIMIT 1"
            else:
                cmd = f"SELECT id, _id, data FROM {self.collection.name} {where_clause} LIMIT 1"
            cursor = self.collection.db.execute(cmd, params)
            row = cursor.fetchone()
            if row:
                int_id, stored_id, data = row
                original_doc = self.collection._load_with_stored_id(
                    int_id, data, stored_id
                )
                self.helpers._internal_replace(int_id, replacement)
                return original_doc
        else:
            # Fallback approach
            if doc := self.find_one(filter):
                int_doc_id = self._get_integer_id_for_oid(doc["_id"])
                self.helpers._internal_replace(int_doc_id, replacement)
                return doc
        return None

    def find_one_and_update(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        """
        Find and update a single document.

        Finds a document matching the given filter, updates it using the specified
        update expression, and returns the original document (before update).

        Args:
            filter (Dict[str, Any]): A dictionary specifying the filter criteria for the document to find.
            update (Dict[str, Any]): A dictionary specifying the update operations to perform on the document.

        Returns:
            Dict[str, Any] | None: The original document (before update),
                                   or None if no document was found and updated.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        filter = self.helpers._normalize_id_query(filter)
        if doc := self.find_one(filter):
            # Get the integer id for the internal operation
            int_doc_id = self._get_integer_id_for_oid(doc["_id"])
            # Update by integer id to avoid conflicts
            where_clause = "WHERE id = ?"
            params = [int_doc_id]
            if self.collection.query_engine._jsonb_supported:
                cmd = f"SELECT id, _id, json(data) as data FROM {self.collection.name} {where_clause} LIMIT 1"
            else:
                cmd = f"SELECT id, _id, data FROM {self.collection.name} {where_clause} LIMIT 1"
            cursor = self.collection.db.execute(cmd, params)
            row = cursor.fetchone()
            if row:
                int_id, stored_id, data = row
                doc_to_update = self.collection._load_with_stored_id(
                    int_id, data, stored_id
                )
                self.helpers._internal_update(int_id, update, doc_to_update)
        return doc

    def count_documents(self, filter: Dict[str, Any]) -> int:
        """
        Return the count of documents that match the given filter.

        Args:
            filter (Dict[str, Any]): A dictionary specifying the query filter.

        Returns:
            int: The number of documents matching the filter.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        filter = self.helpers._normalize_id_query(filter)
        # Try to use SQLTranslator for the WHERE clause
        where_clause, params = self.sql_translator.translate_match(filter)
        if where_clause is not None:
            cmd = f"SELECT COUNT(id) FROM {self.collection.name} {where_clause}"
            row = self.collection.db.execute(cmd, params).fetchone()
            return row[0] if row else 0
        return len(list(self.find(filter)))

    def estimated_document_count(self) -> int:
        """
        Return the estimated number of documents in the collection.

        Returns:
            int: The estimated number of documents.
        """
        row = self.collection.db.execute(
            f"SELECT COUNT(1) FROM {self.collection.name}"
        ).fetchone()
        return row[0] if row else 0

    def distinct(
        self, key: str, filter: Dict[str, Any] | None = None
    ) -> List[Any]:
        """
        Return a list of distinct values from the specified key in the documents
        of this collection, optionally filtered by a query.

        Args:
            key (str): The field name to extract distinct values from.
            filter (Dict[str, Any] | None): An optional query filter to apply to the documents.

        Returns:
            List[Any]: A list containing the distinct values from the specified key.
        """
        # Apply ID type normalization to handle cases where users query 'id' with ObjectId
        if filter is not None:
            filter = self.helpers._normalize_id_query(filter)
        params: List[Any] = []
        where_clause = ""

        if filter:
            # Try to use SQLTranslator for the WHERE clause
            where_clause, params = self.sql_translator.translate_match(filter)

        # For distinct operations, always use json_* functions to avoid binary data issues
        # Even if JSONB is supported, we use json_* for distinct to ensure proper text output
        func_prefix = "json"

        cmd = (
            f"SELECT DISTINCT {func_prefix}_extract(data, '$.{key}') "
            f"FROM {self.collection.name} {where_clause}"
        )
        cursor = self.collection.db.execute(cmd, params)
        results: set[Any] = set()
        for row in cursor.fetchall():
            if row[0] is None:
                continue
            try:
                val = neosqlite_json_loads(row[0])
                match val:
                    case list():
                        results.add(tuple(val))
                    case dict():
                        results.add(neosqlite_json_dumps(val, sort_keys=True))
                    case _:
                        results.add(val)
            except (json.JSONDecodeError, TypeError):
                results.add(row[0])
        return list(results)

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applies a list of aggregation pipeline stages to the collection.

        This method handles both simple and complex queries. For simpler queries,
        it leverages the database's native indexing capabilities to optimize
        performance. For more complex queries, it falls back to a Python-based
        processing mechanism.

        Args:
            pipeline (List[Dict[str, Any]]): A list of aggregation pipeline stages to apply.

        Returns:
            List[Dict[str, Any]]: The list of documents after applying the aggregation pipeline.
        """
        return self.aggregate_with_constraints(pipeline)

    def aggregate_with_constraints(
        self,
        pipeline: List[Dict[str, Any]],
        batch_size: int = 1000,
        memory_constrained: bool = False,
    ) -> List[Dict[str, Any]] | "CompressedQueue":
        """
        Applies a list of aggregation pipeline stages with memory constraints.

        Args:
            pipeline (List[Dict[str, Any]]): A list of aggregation pipeline stages to apply.
            batch_size (int): The batch size for processing large result sets.
            memory_constrained (bool): Whether to use memory-constrained processing.

        Returns:
            List[Dict[str, Any]] | CompressedQueue: The results as either a list or compressed queue.
        """
        # If memory_constrained is True and quez is available, use quez for processing
        if memory_constrained and _HAS_QUEZ:

            # Use quez for memory-constrained processing
            return self._aggregate_with_quez(pipeline, batch_size)

        # Try existing SQL optimization first (this was previously missing)
        try:
            query_result = self.helpers._build_aggregation_query(pipeline)
            if query_result is not None:
                cmd, params, output_fields = query_result
                db_cursor = self.collection.db.execute(cmd, params)
                if output_fields:
                    # Handle results from a GROUP BY query
                    from neosqlite.collection.json_helpers import (
                        neosqlite_json_loads,
                    )

                    results = []
                    for row in db_cursor.fetchall():
                        processed_row = []
                        for i, value in enumerate(row):
                            # If this field contains a JSON array string, parse it
                            # This handles $push and $addToSet results
                            if (
                                output_fields[i] != "_id"
                                and isinstance(value, str)
                                and value.startswith("[")
                                and value.endswith("]")
                            ):
                                try:
                                    processed_row.append(
                                        neosqlite_json_loads(value)
                                    )
                                except Exception:
                                    processed_row.append(value)
                            else:
                                processed_row.append(value)
                        results.append(dict(zip(output_fields, processed_row)))
                    return results
                else:
                    # Handle results from a regular find query
                    return [
                        self.collection._load(row[0], row[1])
                        for row in db_cursor.fetchall()
                    ]
        except Exception:
            # If SQL optimization fails, continue to next approach
            pass

        # Try the temporary table approach for complex pipelines that the
        # current SQL optimization can't handle efficiently
        try:
            from .temporary_table_aggregation import (
                execute_2nd_tier_aggregation,
            )

            # Use the temporary table aggregation which provides enhanced
            # SQL processing for complex pipelines
            return execute_2nd_tier_aggregation(self, pipeline)
        except NotImplementedError:
            # If temporary table approach indicates it needs Python fallback,
            # continue to fallback below
            pass
        except Exception:
            # If temporary table approach fails for other reasons,
            # continue to fallback below
            pass

        # Fallback to old method for complex queries (Python implementation)
        docs: List[Dict[str, Any]] = list(self.find())
        for stage in pipeline:
            stage_name = next(iter(stage.keys()))
            match stage_name:
                case "$match":
                    query = stage["$match"]
                    docs = [
                        doc
                        for doc in docs
                        if self.helpers._apply_query(query, doc)
                    ]
                case "$sort":
                    sort_spec = stage["$sort"]
                    for key, direction in reversed(list(sort_spec.items())):

                        def make_sort_key(key, dir):
                            def sort_key(doc):
                                val = self.collection._get_val(doc, key)
                                # Handle None values - sort them last for ascending, first for descending
                                if val is None:
                                    return (0 if dir == DESCENDING else 1, None)
                                return (0, val)

                            return sort_key

                        sort_key_func = make_sort_key(key, direction)
                        docs.sort(
                            key=sort_key_func,
                            reverse=direction == DESCENDING,
                        )
                case "$skip":
                    count = stage["$skip"]
                    docs = docs[count:]
                case "$limit":
                    count = stage["$limit"]
                    docs = docs[:count]
                case "$project":
                    projection = stage["$project"]
                    docs = [
                        self.helpers._apply_projection(projection, doc)
                        for doc in docs
                    ]
                case "$group":
                    group_spec = stage["$group"]
                    docs = self.helpers._process_group_stage(group_spec, docs)
                case "$unwind":
                    # Handle both string and object forms of $unwind
                    unwind_spec = stage["$unwind"]
                    if isinstance(unwind_spec, str):
                        # Legacy string form
                        field_path = unwind_spec.lstrip("$")
                        include_array_index = None
                        preserve_null_and_empty = False
                    elif isinstance(unwind_spec, dict):
                        # New object form with advanced options
                        field_path = unwind_spec["path"].lstrip("$")
                        include_array_index = unwind_spec.get(
                            "includeArrayIndex"
                        )
                        preserve_null_and_empty = unwind_spec.get(
                            "preserveNullAndEmptyArrays", False
                        )
                    else:
                        raise MalformedQueryException(
                            f"Invalid $unwind specification: {unwind_spec}"
                        )

                    unwound_docs = []
                    for doc in docs:
                        array_to_unwind = self.collection._get_val(
                            doc, field_path
                        )

                        # For nested fields, check if parent exists
                        # If parent is None or missing and we're trying to unwind a nested field,
                        # don't process this document
                        field_parts = field_path.split(".")
                        process_document = True
                        if len(field_parts) > 1:
                            # This is a nested field
                            parent_path = ".".join(field_parts[:-1])
                            parent_value = self.collection._get_val(
                                doc, parent_path
                            )
                            if parent_value is None:
                                # Parent is None or missing, don't process this document
                                process_document = False

                        if not process_document:
                            continue

                        if isinstance(array_to_unwind, list):
                            # Handle array values
                            if array_to_unwind:
                                # Non-empty array - unwind normally
                                for idx, item in enumerate(array_to_unwind):
                                    new_doc = deepcopy(doc)
                                    self.collection._set_val(
                                        new_doc, field_path, item
                                    )
                                    # Add array index if requested
                                    if include_array_index:
                                        new_doc[include_array_index] = idx
                                    unwound_docs.append(new_doc)
                            elif preserve_null_and_empty:
                                # Empty array but preserve is requested
                                new_doc = deepcopy(doc)
                                self.collection._set_val(
                                    new_doc, field_path, None
                                )
                                # Add array index if requested
                                if include_array_index:
                                    new_doc[include_array_index] = None
                                unwound_docs.append(new_doc)
                            # If empty array and preserve is False, don't add any documents
                        elif (
                            not isinstance(array_to_unwind, list)
                            and field_path in doc
                            and preserve_null_and_empty
                        ):
                            # Non-array value (None, string, number, etc.) that exists in the document and preserve is requested
                            new_doc = deepcopy(doc)
                            # Keep the value as-is
                            # Add array index if requested
                            if include_array_index:
                                new_doc[include_array_index] = None
                            unwound_docs.append(new_doc)
                        # Missing fields (field_path not in doc) are never preserved
                        # Default case: non-array values are ignored unless they exist and preserveNullAndEmptyArrays is True
                    docs = unwound_docs
                case "$lookup":
                    # Python fallback implementation for $lookup
                    lookup_spec = stage["$lookup"]
                    from_collection_name = lookup_spec["from"]
                    local_field = lookup_spec["localField"]
                    foreign_field = lookup_spec["foreignField"]
                    as_field = lookup_spec["as"]

                    # Get the from collection from the database
                    from_collection = self.collection._database[
                        from_collection_name
                    ]

                    # Process each document
                    for doc in docs:
                        # Get the local field value
                        local_value = self.collection._get_val(doc, local_field)

                        # Find matching documents in the from collection
                        matching_docs = []
                        for match_doc in from_collection.find():
                            foreign_value = from_collection._get_val(
                                match_doc, foreign_field
                            )
                            if local_value == foreign_value:
                                # Add the matching document (without _id)
                                match_doc_copy = match_doc.copy()
                                match_doc_copy.pop("_id", None)
                                matching_docs.append(match_doc_copy)

                        # Add the matching documents as an array field
                        doc[as_field] = matching_docs
                case "$addFields":
                    add_fields_spec = stage["$addFields"]
                    for doc in docs:
                        for (
                            new_field,
                            source_field,
                        ) in add_fields_spec.items():
                            if isinstance(
                                source_field, str
                            ) and source_field.startswith("$"):
                                source_field_name = source_field[1:]
                                source_value = self.collection._get_val(
                                    doc, source_field_name
                                )
                                self.collection._set_val(
                                    doc, new_field, source_value
                                )
                case _:
                    raise MalformedQueryException(
                        f"Aggregation stage '{stage_name}' not supported"
                    )
        return docs

    def aggregate_raw_batches(
        self,
        pipeline: List[Dict[str, Any]],
        batch_size: int = 100,
    ) -> RawBatchCursor:
        """
        Perform aggregation and retrieve batches of raw JSON.

        Similar to the :meth:`aggregate` method but returns a
        :class:`~neosqlite.raw_batch_cursor.RawBatchCursor`.

        This method returns raw JSON batches which can be more efficient for
        certain use cases where you want to process data in batches rather than
        individual documents.

        Args:
            pipeline (List[Dict[str, Any]]): A list of aggregation pipeline stages to apply.
            batch_size (int): The number of documents to include in each batch.

        Returns:
            RawBatchCursor instance.
        """
        return RawBatchCursor(
            self.collection, None, None, None, batch_size, pipeline=pipeline
        )

    # --- Bulk Write methods ---
    def bulk_write(
        self,
        requests: List[Any],
        ordered: bool = True,
    ) -> BulkWriteResult:
        """
        Execute bulk write operations on the collection.

        Args:
            requests: List of write operations to execute.
            ordered: If true, operations will be performed in order and will
                     raise an exception if a single operation fails.

        Returns:
            BulkWriteResult: A result object containing the number of matched,
                             modified, and inserted documents.
        """
        inserted_count = 0
        matched_count = 0
        modified_count = 0
        deleted_count = 0
        upserted_count = 0

        self.collection.db.execute("SAVEPOINT bulk_write")
        try:
            for req in requests:
                match req:
                    case InsertOne(document=doc):
                        self.insert_one(doc)
                        inserted_count += 1
                    case UpdateOne(filter=f, update=u, upsert=up):
                        update_res = self.update_one(f, u, up)
                        matched_count += update_res.matched_count
                        modified_count += update_res.modified_count
                        if update_res.upserted_id:
                            upserted_count += 1
                    case DeleteOne(filter=f):
                        delete_res = self.delete_one(f)
                        deleted_count += delete_res.deleted_count
            self.collection.db.execute("RELEASE SAVEPOINT bulk_write")
        except Exception as e:
            self.collection.db.execute("ROLLBACK TO SAVEPOINT bulk_write")
            raise e

        return BulkWriteResult(
            inserted_count=inserted_count,
            matched_count=matched_count,
            modified_count=modified_count,
            deleted_count=deleted_count,
            upserted_count=upserted_count,
        )

    def _aggregate_with_quez(
        self, pipeline: List[Dict[str, Any]], batch_size: int = 1000
    ) -> CompressedQueue:
        """
        Process aggregation pipeline with quez compressed queue for memory efficiency.

        Args:
            pipeline (List[Dict[str, Any]]): A list of aggregation pipeline stages to apply.
            batch_size (int): The batch size for quez queue processing.

        Returns:
            CompressedQueue: A compressed queue containing the results.
        """
        try:
            if _HAS_QUEZ:
                from quez import CompressedQueue

                # Create a compressed queue for results with a reasonable size
                # Use unbounded queue to avoid blocking during population
                result_queue = CompressedQueue()

            # Get results from normal aggregation
            results = self.aggregate(pipeline)

            # Add all results to the compressed queue
            for result in results:
                result_queue.put(result)

            return result_queue

        except ImportError:
            # If quez is not available, fall back to normal processing
            # This should never happen since we check for quez availability before calling this method
            raise RuntimeError("Quez is not available but was expected to be")

    def initialize_ordered_bulk_op(self) -> BulkOperationExecutor:
        """Initialize an ordered bulk operation.

        Returns:
            BulkOperationExecutor: An executor for ordered bulk operations.
        """
        return BulkOperationExecutor(self.collection, ordered=True)

    def initialize_unordered_bulk_op(self) -> BulkOperationExecutor:
        """Initialize an unordered bulk operation.

        Returns:
            BulkOperationExecutor: An executor for unordered bulk operations.
        """
        return BulkOperationExecutor(self.collection, ordered=False)
