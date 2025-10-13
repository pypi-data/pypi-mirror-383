import asyncio
from typing import AsyncIterable, Dict, Iterable, List, Optional, Union

from . import results, sync_collection
from .typedefs import *


def _make_wrapped(method):
    async def async_method(self, *args, **kwargs):
        sync_method = getattr(self._collection, method.__name__)

        async with self._db_lock:
            return await asyncio.to_thread(sync_method, *args, **kwargs)

    return async_method


class AsyncCollection:
    """
    Asynchronous wrapper for SyncCollection. While this won't provide any of the
    advantages of actual async queries, this allows code to be written
    asynchronously, and then easily switched to the real MongoDB.
    """

    def __init__(
        self,
        collection: sync_collection.SyncCollection,
        db_lock: asyncio.Lock,
    ):
        self._collection = collection
        self._db_lock = db_lock

    @property
    def name(self) -> str:
        return self._collection.name

    @_make_wrapped
    async def count_all_documents(
        self,
    ) -> int:
        raise RuntimeError("Unreachable")

    @_make_wrapped
    async def count_documents(
        self,
        filter: BsonLike,  # Default value?
        session=None,
        skip: int = 0,
        limit: int = 0,
        maxTimeMs: Optional[int] = None,
        collation=None,
        hint=None,
    ) -> int:
        raise RuntimeError("Unreachable")

    @_make_wrapped
    async def delete_many(
        self, filter: BsonLike, collation=None, hint=None, session=None
    ) -> results.DeleteResult:
        raise RuntimeError("Unreachable")

    @_make_wrapped
    async def delete_one(
        self, filter: BsonLike, collation=None, hint=None, session=None
    ) -> results.DeleteResult:
        raise RuntimeError("Unreachable")

    @_make_wrapped
    async def drop(self):
        pass

    async def find(
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
    ) -> AsyncIterable[BsonLike]:
        result_iter = self._collection.find(
            filter=filter,
            projection=projection,
            skip=skip,
            limit=limit,
            no_cursor_timeout=no_cursor_timeout,
            cursor_type=cursor_type,
            sort=sort,
            allow_partial_results=allow_partial_results,
            oplog_replay=oplog_replay,
            batch_size=batch_size,
            manipulate=manipulate,
            collation=collation,
            show_record_id=show_record_id,
            snapshot=snapshot,
            hint=hint,
            max_time_ms=max_time_ms,
            max_scan=max_scan,
            min=min,
            max=max,
            comment=comment,
            session=session,
            modifiers=modifiers,
            allow_disk_use=allow_disk_use,
        )

        for result in result_iter:
            yield result

    @_make_wrapped
    async def find_one(
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
        pass

    @_make_wrapped
    async def insert_one(
        self,
        document: BsonLike,
        bypass_document_validation: bool = False,
        session: bool = None,
    ) -> results.InsertOneResult:
        raise RuntimeError("Unreachable")

    @_make_wrapped
    async def insert_many(
        self,
        documents: Iterable[BsonLike],
        ordered: bool = True,
        bypass_document_validation: bool = False,
        session: bool = None,
    ) -> results.InsertManyResult:
        raise RuntimeError("Unreachable")

    @_make_wrapped
    async def replace_one(
        self,
        filter: BsonLike,
        replacement: BsonLike,
        upsert=False,
        bypass_document_validation=False,
        collation=None,
        hint=None,
        session=None,
    ) -> results.UpdateResult:
        raise RuntimeError("Unreachable")

    @_make_wrapped
    async def update_one(
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
        raise RuntimeError("Unreachable")

    @_make_wrapped
    async def update_many(
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
        raise RuntimeError("Unreachable")
