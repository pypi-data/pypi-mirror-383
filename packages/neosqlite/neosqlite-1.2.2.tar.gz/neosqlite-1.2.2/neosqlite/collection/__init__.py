from __future__ import annotations
from ..bulk_operations import BulkOperationExecutor
from ..changestream import ChangeStream
from ..objectid import ObjectId
from ..results import (
    BulkWriteResult,
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)
from .aggregation_cursor import AggregationCursor
from .cursor import Cursor
from .index_manager import IndexManager
from .query_engine import QueryEngine
from .raw_batch_cursor import RawBatchCursor
from neosqlite.collection.json_helpers import neosqlite_json_loads
from typing import Any, Dict, List, Tuple, Union, overload
from typing_extensions import Literal

try:
    from pysqlite3 import dbapi2 as sqlite3
except ImportError:
    import sqlite3  # type: ignore


class Collection:
    """
    Provides a class representing a collection in a SQLite database.

    This class encapsulates operations on a collection such as inserting,
    updating, deleting, and querying documents.
    """

    def __init__(
        self,
        db: sqlite3.Connection,
        name: str,
        create: bool = True,
        database=None,
    ):
        """
        Initialize a new collection object.

        Args:
            db: Database object to which the collection belongs.
            name: Name of the collection.
            create: Whether to create the collection table if it doesn't exist.
            database: Database object that contains this collection.
        """
        self.db = db
        self.name = name
        self._database = database
        self.indexes = IndexManager(self)
        self.query_engine = QueryEngine(self)

        if create:
            self.create()

    # --- Collection helper methods ---
    def _load(self, id: int, data: str | bytes) -> Dict[str, Any]:
        """
        Deserialize and load a document from its ID and JSON data.

        Deserialize the JSON string or bytes back into a Python dictionary,
        add the document ID to it, and return the document.

        Args:
            id (int): The document ID.
            data (str | bytes): The JSON string or bytes representing the document.

        Returns:
            Dict[str, Any]: The deserialized document with the _id field added.
        """
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        document: Dict[str, Any] = neosqlite_json_loads(data)
        # Try to get the _id from the dedicated _id column first, otherwise use the auto-increment id
        _id = self._get_stored_id(id)
        document["_id"] = _id if _id is not None else id
        return document

    def _load_with_stored_id(
        self, id_val: int, data: str | bytes, stored_id_val
    ) -> Dict[str, Any]:
        """
        Deserialize and load a document with the stored _id value.

        Args:
            id_val (int): The auto-increment document ID.
            data (str | bytes): The JSON string or bytes representing the document.
            stored_id_val: The stored _id value from the _id column.

        Returns:
            Dict[str, Any]: The deserialized document with the _id field added.
        """
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        document: Dict[str, Any] = neosqlite_json_loads(data)

        # Use the stored _id value if available, otherwise fall back to the auto-increment id
        _id: Union[ObjectId, Any]
        if stored_id_val is not None:
            # Try to decode as ObjectId if it looks like one
            if isinstance(stored_id_val, str) and len(stored_id_val) == 24:
                try:
                    _id = ObjectId(stored_id_val)
                except ValueError:
                    _id = stored_id_val
            else:
                _id = stored_id_val
        else:
            # Fallback to the auto-increment ID for backward compatibility
            _id = id_val

        document["_id"] = _id
        return document

    def _get_stored_id(self, doc_id: int) -> ObjectId | int | str | None:
        """
        Retrieve the stored _id for a document from the _id column.

        Args:
            doc_id (int): The document ID.

        Returns:
            ObjectId | int | None: The stored _id value, or None if the column doesn't exist yet.
        """
        try:
            # Check if the _id column exists
            cursor = self.db.execute(
                f"SELECT name FROM pragma_table_info('{self.name}') WHERE name = '_id'"
            )
            column_exists = cursor.fetchone() is not None

            if column_exists:
                cursor = self.db.execute(
                    f"SELECT _id FROM {self.name} WHERE id = ?", (doc_id,)
                )
                row = cursor.fetchone()
                if row and row[0] is not None:
                    stored_id = row[0]
                    # Try to decode as ObjectId if it matches ObjectId format
                    if isinstance(stored_id, str) and len(stored_id) == 24:
                        try:
                            return ObjectId(stored_id)
                        except ValueError:
                            # Not a valid ObjectId, return as-is
                            return stored_id
                    return stored_id
                else:
                    # If no row is found or row[0] is None, return None
                    return None
            else:
                # For backward compatibility, if _id column doesn't exist, return the original ID
                return doc_id
        except Exception:
            # If there's any error retrieving the _id, return None
            return None

    def _get_val(self, item: Dict[str, Any], key: str) -> Any:
        """
        Retrieves a value from a dictionary using a key, handling nested keys and
        optional prefixes.

        Args:
            item (Dict[str, Any]): The dictionary to search.
            key (str): The key to retrieve, may include nested keys separated by
                       dots or may be prefixed with '$'.

        Returns:
            Any: The value associated with the key, or None if the key is not found.
        """
        if key.startswith("$"):
            key = key[1:]
        val: Any = item
        for k in key.split("."):
            if val is None:
                return None
            val = val.get(k)
        return val

    def _set_val(self, item: Dict[str, Any], key: str, value: Any) -> None:
        """
        Sets a value in a dictionary using a key, handling nested keys and
        optional prefixes.

        Args:
            item (Dict[str, Any]): The dictionary to modify.
            key (str): The key to set, may include nested keys separated by dots
                       or may be prefixed with \'$.
            value (Any): The value to set.
        """
        if key.startswith("$"):
            key = key[1:]

        keys = key.split(".")
        current = item

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]

        # Set the value at the target key
        current[keys[-1]] = value

    # --- Collection methods ---
    def create(self):
        """
        Initialize the collection table if it does not exist.

        This method creates a table with an 'id' column, a '_id' column for
        ObjectId storage, and a 'data' column for storing JSON data.
        If the JSONB data type is supported, it will be used,
        otherwise, TEXT data type will be used.
        """
        # Use the QueryEngine's cached JSONB support flag
        if self.query_engine._jsonb_supported:
            self.db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    _id JSONB,
                    data JSONB NOT NULL
                )"""
            )
        else:
            self.db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    _id TEXT,
                    data TEXT NOT NULL
                )
                """
            )

        # Create unique index on _id column for faster lookups
        try:
            self.db.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{self.name}_id ON {self.name}(_id)"
            )
        except Exception:
            # If we can't create the index (e.g., due to duplicate values), continue without it
            pass

        # Add the _id column if it doesn't exist (for backward compatibility)
        self._ensure_id_column_exists()

        # Create unique index on _id column for faster lookups
        self._create_unique_index_for_id()

    def _ensure_id_column_exists(self):
        """
        Ensure that the _id column exists in the collection table for backward compatibility.
        """
        try:
            # Check if _id column exists
            cursor = self.db.execute(
                f"SELECT name FROM pragma_table_info('{self.name}') WHERE name = '_id'"
            )
            column_exists = cursor.fetchone() is not None

            if not column_exists:
                # Add the _id column using the same type as the data column
                if self.query_engine._jsonb_supported:
                    self.db.execute(
                        f"ALTER TABLE {self.name} ADD COLUMN _id JSONB"
                    )
                else:
                    self.db.execute(
                        f"ALTER TABLE {self.name} ADD COLUMN _id TEXT"
                    )
                # Create unique index on _id column for faster lookups
                self._create_unique_index_for_id()
        except Exception:
            # If we can't add the column, continue without it (for backward compatibility)
            pass

    def _create_unique_index_for_id(self):
        """
        Create unique index on _id column for faster lookups.
        """
        try:
            # Create unique index on _id column for faster lookups
            self.db.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{self.name}_id ON {self.name}(_id)"
            )
        except Exception:
            # If we can't create the index (e.g., due to duplicate values), continue without it
            pass

    def rename(self, new_name: str) -> None:
        """
        Renames the collection to the specified new name.
        If the new name is the same as the current name, does nothing.

        Checks if a table with the new name exists and raises an error if it does.
        Renames the underlying table and updates the collection's name.

        Args:
            new_name (str): The new name for the collection.

        Raises:
            sqlite3.Error: If a collection with the new name already exists.
        """
        # If the new name is the same as the current name, do nothing
        if new_name == self.name:
            return

        # Check if a collection with the new name already exists
        if self._object_exists(type_="table", name=new_name):
            raise sqlite3.Error(f"Collection '{new_name}' already exists")

        # Rename the table
        self.db.execute(f"ALTER TABLE {self.name} RENAME TO {new_name}")

        # Update the collection name
        self.name = new_name

    def options(self) -> Dict[str, Any]:
        """
        Retrieves options set on this collection.

        Returns:
            dict: A dictionary containing various options for the collection,
                including the table's name, columns, indexes, and count of documents.
        """
        # For SQLite, we can provide information about the table structure
        options: Dict[str, Any] = {
            "name": self.name,
        }

        # Get table information
        try:
            # Get table info
            table_info = self.db.execute(
                f"PRAGMA table_info({self.name})"
            ).fetchall()
            options["columns"] = [
                {
                    "name": str(col[1]),
                    "type": str(col[2]),
                    "notnull": bool(col[3]),
                    "default": col[4],
                    "pk": bool(col[5]),
                }
                for col in table_info
            ]

            # Get index information
            indexes = self.db.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name=?",
                (self.name,),
            ).fetchall()
            options["indexes"] = [
                {
                    "name": str(idx[0]),
                    "definition": str(idx[1]) if idx[1] is not None else "",
                }
                for idx in indexes
            ]

            # Get row count
            if count_row := self.db.execute(
                f"SELECT COUNT(*) FROM {self.name}"
            ).fetchone():
                options["count"] = (
                    int(count_row[0]) if count_row[0] is not None else 0
                )
            else:
                options["count"] = 0

        except sqlite3.Error:
            # If we can't get detailed information, return basic info
            options["columns"] = []
            options["indexes"] = []
            options["count"] = 0

        return options

    # --- Querying methods delegated to QueryEngine ---
    def insert_one(self, document: Dict[str, Any]) -> InsertOneResult:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.insert_one`.
        """
        return self.query_engine.insert_one(document)

    def insert_many(self, documents: List[Dict[str, Any]]) -> InsertManyResult:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.insert_many`.
        """
        return self.query_engine.insert_many(documents)

    def update_one(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> UpdateResult:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.update_one`.
        """
        return self.query_engine.update_one(filter, update, upsert)

    def update_many(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> UpdateResult:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.update_many`.
        """
        return self.query_engine.update_many(filter, update)

    def replace_one(
        self,
        filter: Dict[str, Any],
        replacement: Dict[str, Any],
        upsert: bool = False,
    ) -> UpdateResult:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.replace_one`.
        """
        return self.query_engine.replace_one(filter, replacement, upsert)

    def delete_one(self, filter: Dict[str, Any]) -> DeleteResult:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.delete_one`.
        """
        return self.query_engine.delete_one(filter)

    def delete_many(self, filter: Dict[str, Any]) -> DeleteResult:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.delete_many`.
        """
        return self.query_engine.delete_many(filter)

    def find(
        self,
        filter: Dict[str, Any] | None = None,
        projection: Dict[str, Any] | None = None,
        hint: str | None = None,
    ) -> Cursor:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.find`.
        """
        return self.query_engine.find(filter, projection, hint)

    def find_raw_batches(
        self,
        filter: Dict[str, Any] | None = None,
        projection: Dict[str, Any] | None = None,
        hint: str | None = None,
        batch_size: int = 100,
    ) -> RawBatchCursor:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.find_raw_batches`.
        """
        return self.query_engine.find_raw_batches(
            filter, projection, hint, batch_size
        )

    def find_one(
        self,
        filter: Dict[str, Any] | None = None,
        projection: Dict[str, Any] | None = None,
        hint: str | None = None,
    ) -> Dict[str, Any] | None:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.find_one`.
        """
        return self.query_engine.find_one(filter, projection, hint)

    def count_documents(self, filter: Dict[str, Any]) -> int:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.count_documents`.
        """
        return self.query_engine.count_documents(filter)

    def estimated_document_count(self) -> int:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.estimated_document_count`.
        """
        return self.query_engine.estimated_document_count()

    def find_one_and_delete(
        self,
        filter: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.find_one_and_delete`.
        """
        return self.query_engine.find_one_and_delete(filter)

    def find_one_and_replace(
        self,
        filter: Dict[str, Any],
        replacement: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.find_one_and_replace`.
        """
        return self.query_engine.find_one_and_replace(filter, replacement)

    def find_one_and_update(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.find_one_and_update`.
        """
        return self.query_engine.find_one_and_update(filter, update)

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> AggregationCursor:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.aggregate`.
        """
        return AggregationCursor(self, pipeline)

    def aggregate_raw_batches(
        self,
        pipeline: List[Dict[str, Any]],
        batch_size: int = 100,
    ) -> RawBatchCursor:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.aggregate_raw_batches`.
        """
        return self.query_engine.aggregate_raw_batches(pipeline, batch_size)

    def distinct(
        self, key: str, filter: Dict[str, Any] | None = None
    ) -> List[Any]:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.distinct`.
        """
        return self.query_engine.distinct(key, filter)

    # --- Bulk Write methods delegated to QueryEngine ---
    def bulk_write(
        self,
        requests: List[Any],
        ordered: bool = True,
    ) -> BulkWriteResult:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.bulk_write`.
        """
        return self.query_engine.bulk_write(requests, ordered)

    def initialize_ordered_bulk_op(self) -> BulkOperationExecutor:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.initialize_ordered_bulk_op`.
        """
        return self.query_engine.initialize_ordered_bulk_op()

    def initialize_unordered_bulk_op(self) -> BulkOperationExecutor:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.query_engine.QueryEngine.initialize_unordered_bulk_op`.
        """
        return self.query_engine.initialize_unordered_bulk_op()

    # --- Indexing methods delegated to IndexManager ---
    def create_index(
        self,
        key: str | List[str],
        reindex: bool = True,
        sparse: bool = False,
        unique: bool = False,
        fts: bool = False,
        tokenizer: str | None = None,
        datetime_field: bool = False,
    ):
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.create_index`.
        """
        self.indexes.create_index(
            key, reindex, sparse, unique, fts, tokenizer, datetime_field
        )

    def create_search_index(
        self,
        key: str,
        tokenizer: str | None = None,
    ):
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.create_search_index`.
        """
        return self.indexes.create_search_index(key, tokenizer)

    def create_indexes(
        self,
        indexes: List[str | List[str] | List[Tuple[str, int]] | Dict[str, Any]],
    ) -> List[str]:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.create_indexes`.
        """
        return self.indexes.create_indexes(indexes)

    def create_search_indexes(
        self,
        indexes: List[str],
    ) -> List[str]:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.create_search_indexes`.
        """
        return self.indexes.create_search_indexes(indexes)

    def reindex(
        self,
        table: str,
        sparse: bool = False,
        documents: List[Dict[str, Any]] | None = None,
    ):
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.reindex`.
        """
        self.indexes.reindex(table, sparse, documents)

    @overload
    def list_indexes(self, as_keys: Literal[True]) -> List[List[str]]: ...
    @overload
    def list_indexes(self, as_keys: Literal[False] = False) -> List[str]: ...
    def list_indexes(
        self,
        as_keys: bool = False,
    ) -> List[str] | List[List[str]]:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.list_indexes`.
        """
        # This explicit check is the key to solving the Mypy error on overloading.
        if as_keys:
            # Inside this block, Mypy knows 'as_keys' is Literal[True].
            return self.indexes.list_indexes(as_keys)
        else:
            # Inside this block, Mypy knows 'as_keys' is Literal[False].
            return self.indexes.list_indexes(as_keys)

    def list_search_indexes(self) -> List[str]:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.list_search_indexes`.
        """
        return self.indexes.list_search_indexes()

    def update_search_index(self, key: str, tokenizer: str | None = None):
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.update_search_index`.
        """
        self.indexes.update_search_index(key, tokenizer)

    def drop_index(self, index: str):
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.drop_index`.
        """
        self.indexes.drop_index(index)

    def drop_search_index(self, index: str):
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.drop_search_index`.
        """
        self.indexes.drop_search_index(index)

    def drop_indexes(self):
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.drop_indexes`.
        """
        self.indexes.drop_indexes()

    def index_information(self) -> Dict[str, Any]:
        """
        This is a delegating method. For implementation details, see the
        core logic in :meth:`~neosqlite.collection.index_manager.IndexManager.index_information`.
        """
        return self.indexes.index_information()

    # --- Other methods ---
    @property
    def database(self):
        """
        Get the database that this collection is a part of.

        Returns:
            Connection: The connection object this collection is associated with.
        """
        return self._database

    def _object_exists(self, type_: str, name: str) -> bool:
        """
        Check if an object (table or index) of a specific type and name exists within the database.

        Args:
            type_ (str): The type of object to check, either "table" or "index".
            name (str): The name of the object to check.

        Returns:
            bool: True if the object exists, False otherwise.
        """
        match type_:
            case "table":
                if row := self.db.execute(
                    "SELECT COUNT(1) FROM sqlite_master WHERE type = ? AND name = ?",
                    (type_, name.strip("[]")),
                ).fetchone():
                    return int(row[0]) > 0
                return False
            case "index":
                # For indexes, check if it exists with our naming convention
                if row := self.db.execute(
                    "SELECT COUNT(1) FROM sqlite_master WHERE type = ? AND name = ?",
                    (type_, name),
                ).fetchone():
                    return int(row[0]) > 0
                return False
            case _:
                return False

    def drop(self):
        """
        Drop the entire collection.

        This method removes the collection (table) from the database. After calling
        this method, the collection will no longer exist in the database.
        """
        self.db.execute(f"DROP TABLE IF EXISTS {self.name}")

    def watch(
        self,
        pipeline: List[Dict[str, Any]] | None = None,
        full_document: str | None = None,
        resume_after: Dict[str, Any] | None = None,
        max_await_time_ms: int | None = None,
        batch_size: int | None = None,
        collation: Dict[str, Any] | None = None,
        start_at_operation_time: Any | None = None,
        session: Any | None = None,
        start_after: Dict[str, Any] | None = None,
    ) -> ChangeStream:
        """
        Monitor changes on this collection using SQLite's change tracking features.

        This method creates a change stream that allows iterating over change events
        generated by modifications to the collection. While SQLite doesn't natively
        support change streams like MongoDB, this implementation uses triggers and
        SQLite's built-in change tracking mechanisms to provide similar functionality.

        Args:
            pipeline (List[Dict[str, Any]]): Aggregation pipeline stages to apply to change events.
            full_document (str): Determines how the 'fullDocument' field is populated in change events.
            resume_after (Dict[str, Any]): Logical starting point for the change stream.
            max_await_time_ms (int): Maximum time to wait for new documents in milliseconds.
            batch_size (int): Number of documents to return per batch.
            collation (Dict[str, Any]): Collation settings for the operation.
            start_at_operation_time (Any): Operation time to start monitoring from.
            session (Any): Client session for the operation.
            start_after (Dict[str, Any]): Logical starting point for the change stream.

        Returns:
            ChangeStream: A change stream object that can be iterated over to receive change events.
        """
        return ChangeStream(
            collection=self,
            pipeline=pipeline,
            full_document=full_document,
            resume_after=resume_after,
            max_await_time_ms=max_await_time_ms,
            batch_size=batch_size,
            collation=collation,
            start_at_operation_time=start_at_operation_time,
            session=session,
            start_after=start_after,
        )
