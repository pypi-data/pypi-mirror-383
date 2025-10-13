from typing import Any, Dict, Iterable, List, Optional, Union

from . import native, results, sync_database
from .typedefs import *


def _unsupported(name: str, value: Any, default: Any):
    if value != default:
        print(f'Warning: The "{name}" parameter is not supported and will be ignored.')


class SyncCollection:
    def __init__(self, _db: "sync_database.SyncDatabase", name: str):
        self._db = _db
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def _notify_persistence_of_change(
        self,
        result: Union[
            results.DeleteResult,
            results.UpdateResult,
            results.InsertOneResult,
            results.InsertManyResult,
        ],
    ):
        # Check if a change was actually made
        if isinstance(result, results.DeleteResult) and result.n_deleted == 0:
            return

        if isinstance(result, results.UpdateResult) and result.modified_count == 0:
            return

        if isinstance(result, results.InsertOneResult) and result.inserted_id is None:
            return

        if isinstance(result, results.InsertManyResult) and not result.inserted_ids:
            return

        # Something has changed, notify the persistence
        if self._db._persistence is not None:
            self._db._persistence.notify_change()

    def count_all_documents(
        self,
    ) -> int:
        call_result = native.collection_count_all_documents(
            self._db._rust_db,
            self._name.encode("utf-8"),
        )
        return native.wrapped_bson.consume_into_response(call_result)  # type: ignore

    def count_documents(
        self,
        filter: BsonLike,  # Default value?
        session=None,
        skip: int = 0,
        limit: int = 0,
        maxTimeMs: Optional[int] = None,
        collation=None,
        hint=None,
    ) -> int:
        _unsupported("session", session, None)
        _unsupported("maxTimeMs", maxTimeMs, None)
        _unsupported("collation", collation, None)
        _unsupported("hint", hint, None)

        call_result = native.collection_count_documents(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson(filter),
            skip,
            limit,
        )
        return native.wrapped_bson.consume_into_response(call_result)  # type: ignore

    def delete_many(
        self, filter: BsonLike, collation=None, hint=None, session=None
    ) -> results.DeleteResult:
        _unsupported("session", session, None)
        _unsupported("collation", collation, None)
        _unsupported("hint", hint, None)

        call_result = native.collection_delete_many(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson(filter),
        )

        call_result = native.wrapped_bson.consume_into_response(call_result)
        call_result = results.DeleteResult.decode(call_result)
        self._notify_persistence_of_change(call_result)
        return call_result

    def delete_one(
        self, filter: BsonLike, collation=None, hint=None, session=None
    ) -> results.DeleteResult:
        _unsupported("session", session, None)
        _unsupported("collation", collation, None)
        _unsupported("hint", hint, None)

        call_result = native.collection_delete_one(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson(filter),
        )

        call_result = native.wrapped_bson.consume_into_response(call_result)
        call_result = results.DeleteResult.decode(call_result)
        self._notify_persistence_of_change(call_result)
        return call_result

    def drop(self):
        self._db.drop_collection(self._name)

    def find(
        self,
        filter: BsonLike = {},
        projection: Union[List[str], Dict[str, bool]] = {},
        skip: int = 0,
        limit: int = 0,
        no_cursor_timeout: bool = False,
        cursor_type: str = "non_tailable",
        sort: SortList = [],
        allow_partial_results: bool = False,
        oplog_replay: bool = False,
        batch_size: Optional[int] = None,
        manipulate: Optional[bool] = None,
        collation=None,
        show_record_id: bool = False,
        snapshot: bool = False,
        hint=None,
        max_time_ms: Optional[int] = None,
        max_scan: Optional[int] = None,
        min=None,
        max=None,
        comment: Optional[str] = None,
        session=None,
        modifiers: dict = {},
        allow_disk_use: bool = False,
    ) -> Iterable[BsonLike]:
        _unsupported("no_cursor_timeout", no_cursor_timeout, False)
        _unsupported("cursor_type", cursor_type, "non_tailable")
        _unsupported("allow_partial_results", allow_partial_results, False)
        _unsupported("oplog_replay", oplog_replay, False)
        _unsupported("batch_size", batch_size, None)
        _unsupported("manipulate", manipulate, None)
        _unsupported("collation", collation, None)
        _unsupported("show_record_id", show_record_id, False)
        _unsupported("snapshot", snapshot, False)
        _unsupported("hint", hint, None)
        _unsupported("max_time_ms", max_time_ms, None)
        _unsupported("max_scan", max_scan, None)
        _unsupported("min", min, None)
        _unsupported("max", max, None)
        _unsupported("comment", comment, None)
        _unsupported("session", session, None)
        _unsupported("modifiers", modifiers, {})
        _unsupported("allow_disk_use", allow_disk_use, False)

        call_result = native.collection_find(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson(filter),
            native.wrapped_bson.from_bson({"projection": projection}),
            skip,
            limit,
            native.wrapped_bson.from_bson({"sort": sort}),
        )
        return native.wrapped_bson.consume_into_response(call_result)  # type: ignore

    def find_one(
        self,
        filter: BsonLike = {},
        projection: Union[List[str], Dict[str, bool]] = {},
        skip: int = 0,
        limit: int = 0,
        no_cursor_timeout: bool = False,
        cursor_type: str = "non_tailable",
        sort: SortList = [],
        allow_partial_results: bool = False,
        oplog_replay: bool = False,
        batch_size: Optional[int] = None,
        manipulate: Optional[bool] = None,
        collation=None,
        show_record_id: bool = False,
        snapshot: bool = False,
        hint=None,
        max_time_ms: Optional[int] = None,
        max_scan: Optional[int] = None,
        min=None,
        max=None,
        comment: Optional[str] = None,
        session=None,
        modifiers: dict = {},
        allow_disk_use: bool = False,
    ) -> Optional[BsonLike]:
        if limit not in (0, 1):
            print(f"Warning: Using `find_one` with a limit of `{limit}`!")

        _unsupported("no_cursor_timeout", no_cursor_timeout, False)
        _unsupported("cursor_type", cursor_type, "non_tailable")
        _unsupported("allow_partial_results", allow_partial_results, False)
        _unsupported("oplog_replay", oplog_replay, False)
        _unsupported("batch_size", batch_size, None)
        _unsupported("manipulate", manipulate, None)
        _unsupported("collation", collation, None)
        _unsupported("show_record_id", show_record_id, False)
        _unsupported("snapshot", snapshot, False)
        _unsupported("hint", hint, None)
        _unsupported("max_time_ms", max_time_ms, None)
        _unsupported("max_scan", max_scan, None)
        _unsupported("min", min, None)
        _unsupported("max", max, None)
        _unsupported("comment", comment, None)
        _unsupported("session", session, None)
        _unsupported("modifiers", modifiers, {})
        _unsupported("allow_disk_use", allow_disk_use, False)

        call_result = native.collection_find_one(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson(filter),
            native.wrapped_bson.from_bson({"projection": projection}),
            skip,
            native.wrapped_bson.from_bson({"sort": sort}),
        )
        return native.wrapped_bson.consume_into_response(call_result)

    def insert_one(
        self,
        document: BsonLike,
        bypass_document_validation: bool = False,
        session: bool = None,
    ) -> results.InsertOneResult:
        _unsupported("bypass_document_validation", bypass_document_validation, False)
        _unsupported("session", session, None)

        call_result = native.collection_insert_one(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson(document),
        )

        call_result = native.wrapped_bson.consume_into_response(call_result)
        call_result = results.InsertOneResult.decode(call_result)
        self._notify_persistence_of_change(call_result)
        return call_result

    def insert_many(
        self,
        documents: Iterable[BsonLike],
        ordered: bool = True,
        bypass_document_validation: bool = False,
        session: bool = None,
    ) -> results.InsertManyResult:
        # "ordered" is ignored, but insertions in Not Mongo are always ordered
        # anyways.
        _unsupported("bypass_document_validation", bypass_document_validation, False)
        _unsupported("session", session, None)

        call_result = native.collection_insert_many(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson({"documents": list(documents)}),
        )

        call_result = native.wrapped_bson.consume_into_response(call_result)
        call_result = results.InsertManyResult.decode(call_result)
        self._notify_persistence_of_change(call_result)
        return call_result

    def replace_one(
        self,
        filter: BsonLike,
        replacement: BsonLike,
        upsert=False,
        bypass_document_validation=False,
        collation=None,
        hint=None,
        session=None,
    ) -> results.UpdateResult:
        _unsupported("bypass_document_validation", bypass_document_validation, False)
        _unsupported("collaction", collation, None)
        _unsupported("hint", hint, None)
        _unsupported("session", session, None)

        call_result = native.collection_replace_one(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson(filter),
            native.wrapped_bson.from_bson(replacement),
            upsert,
        )

        call_result = native.wrapped_bson.consume_into_response(call_result)
        call_result = results.UpdateResult.decode(call_result)
        self._notify_persistence_of_change(call_result)
        return call_result

    def update_one(
        self,
        filter: BsonLike,
        update: BsonLike,
        upsert=False,
        bypass_document_validation=False,
        collation=None,
        array_filters=None,
        hint=None,
        session=None,
    ) -> results.UpdateResult:
        _unsupported("bypass_document_validation", bypass_document_validation, False)
        _unsupported("collaction", collation, None)
        _unsupported("array_filters", array_filters, None)
        _unsupported("hint", hint, None)
        _unsupported("session", session, None)

        call_result = native.collection_update_one(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson(filter),
            native.wrapped_bson.from_bson(update),
            upsert,
        )

        call_result = native.wrapped_bson.consume_into_response(call_result)
        call_result = results.UpdateResult.decode(call_result)
        self._notify_persistence_of_change(call_result)
        return call_result

    def update_many(
        self,
        filter: BsonLike,
        update: BsonLike,
        upsert=False,
        bypass_document_validation=False,
        collation=None,
        array_filters=None,
        hint=None,
        session=None,
    ) -> results.UpdateResult:
        _unsupported("bypass_document_validation", bypass_document_validation, False)
        _unsupported("collation", collation, None)
        _unsupported("array_filters", array_filters, None)
        _unsupported("hint", hint, None)
        _unsupported("session", session, None)

        call_result = native.collection_update_many(
            self._db._rust_db,
            self._name.encode("utf-8"),
            native.wrapped_bson.from_bson(filter),
            native.wrapped_bson.from_bson(update),
            upsert,
        )

        call_result = native.wrapped_bson.consume_into_response(call_result)
        call_result = results.UpdateResult.decode(call_result)
        self._notify_persistence_of_change(call_result)
        return call_result
