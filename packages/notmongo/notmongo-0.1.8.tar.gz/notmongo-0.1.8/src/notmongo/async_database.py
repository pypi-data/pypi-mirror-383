import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional

from . import async_collection, persistence, sync_database
from .typedefs import *


class AsyncDatabase:
    """
    Asynchronous equivalent for SyncDatabase. Method calls are  the same as for
    SyncDatabase , but instead of SyncCollections, this class returns
    AsyncCollections.


    This doesn't provide the the advantages of actual async operations, but
    allows code to be written asynchronously, and then easily switched to the
    real MongoDB.
    """

    def __init__(self):
        self._sync_db = sync_database.SyncDatabase()
        self._db_lock = asyncio.Lock()

    @property
    def persistence(self) -> Optional[persistence.BasePersistence]:
        return self._sync_db.persistence

    @persistence.setter
    def persistence(self, value: "persistence.BasePersistence"):
        self._sync_db.persistence = value

    @classmethod
    def load_json(
        cls,
        path: Union[Path, str],
        *,
        compression: Compression = None,
    ) -> "AsyncDatabase":
        # TODO: Make async?
        result = AsyncDatabase()
        result._sync_db = sync_database.SyncDatabase.load_json(
            path,
            compression=compression,
        )
        return result

    @classmethod
    def loads_json(cls, serialized: str) -> "AsyncDatabase":
        # TODO: Make async?
        result = AsyncDatabase()
        result._sync_db = sync_database.SyncDatabase.loads_json(serialized)
        return result

    @classmethod
    def load_bson(
        cls,
        path: Path,
        compression: Compression,
    ) -> "AsyncDatabase":
        # TODO: Make async?
        result = AsyncDatabase()
        result._sync_db = sync_database.SyncDatabase.load_bson(
            path,
            compression=compression,
        )
        return result

    @classmethod
    def loads_bson(cls, contents: bytes) -> "AsyncDatabase":
        # TODO: Make async?
        result = AsyncDatabase()
        result._sync_db = sync_database.SyncDatabase.loads_bson(contents)
        return result

    def dump_json(
        self,
        path: Path,
        *,
        relaxed: bool = True,
        format: bool = False,
        n_backups: int = 0,
        compression: Compression = None,
    ) -> None:
        # TODO: Make async?
        self._sync_db.dump_json(
            path,
            relaxed=relaxed,
            format=format,
            n_backups=n_backups,
            compression=compression,
        )

    def dumps_json(self, relaxed: bool = True, format: bool = False) -> str:
        # TODO: Make async?
        return self._sync_db.dumps_json(relaxed=relaxed, format=format)

    def dump_bson(
        self,
        path: Path,
        *,
        n_backups: int = 0,
        compression: Compression = None,
    ) -> None:
        # TODO: Make async?
        self._sync_db.dump_bson(
            path,
            n_backups=n_backups,
            compression=compression,
        )

    def dumps_bson(self) -> bytes:
        # TODO: Make async?
        return self._sync_db.dumps_bson()

    async def n_collections(self) -> int:
        # This is a fast operation, no point in using a thread
        return self._sync_db.n_collections()

    async def collections(
        self,
    ) -> AsyncGenerator["async_collection.AsyncCollection", None]:
        # This is a fast operation, no point in using a thread
        for scol in self._sync_db.collections():
            yield async_collection.AsyncCollection(scol, self._db_lock)

    def collection(self, collection_name: str) -> "async_collection.AsyncCollection":
        if not isinstance(collection_name, str):
            raise TypeError("The collection name has to be a string.")

        return async_collection.AsyncCollection(
            self._sync_db.collection(collection_name),
            self._db_lock,
        )

    async def drop_collection(self, collection_name: str) -> None:
        # This is a fast operation, no point in using a thread
        self._sync_db.drop_collection(collection_name)

    def __getitem__(self, collection_name: str) -> "async_collection.AsyncCollection":
        return self.collection(collection_name)
