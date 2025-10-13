import ctypes
from pathlib import Path
from typing import *  # type: ignore

import bson

from . import native, persistence, sync_collection
from .typedefs import *


class SyncDatabase:
    def __init__(self):
        self._rust_db: ctypes.c_void_p = native.db_new_empty()
        self._persistence: Optional[persistence.BasePersistence] = None

    @property
    def persistence(self) -> Optional[persistence.BasePersistence]:
        return self._persistence

    @persistence.setter
    def persistence(self, value: "persistence.BasePersistence"):
        if not isinstance(value, persistence.BasePersistence):
            raise TypeError(value)

        if self._persistence is not None:
            self._persistence.save_now()
            self._persistence.db = None

        self._persistence = value
        self._persistence.db = self

    @classmethod
    def load_json(
        cls,
        path: Union[Path, str],
        *,
        compression: Compression = None,
    ) -> "SyncDatabase":
        # FIXME: "load" should really accept a file-like object, not a path!

        if isinstance(path, str):
            path = Path(path)

        if not isinstance(path, Path):
            raise TypeError("The path has to be a Path or a string.")

        # Load the contents
        result = SyncDatabase()
        call_result = native.db_populate_from_json_file(
            result._rust_db,
            str(path.resolve()).encode("utf-8"),
            native.compression_to_int(compression),
        )

        # Check for errors
        call_result.consume_into_response()
        return result

    @classmethod
    def loads_json(cls, serialized: str) -> "SyncDatabase":
        if not isinstance(serialized, str):
            raise TypeError(serialized)

        # Load the contents
        result = SyncDatabase()
        call_result = native.db_populate_from_json_string(
            result._rust_db,
            native.wrapped_bson.from_bson({"contents": serialized}),
        )

        # Check for errors
        call_result.consume_into_response()
        return result

    @classmethod
    def load_bson(
        cls,
        path: Path,
        *,
        compression: Compression,
    ) -> "SyncDatabase":
        # FIXME: "load" should really accept a file-like object, not a path!

        if isinstance(path, str):
            path = Path(path)

        if not isinstance(path, Path):
            raise TypeError("The path has to be a Path or a string.")

        # Load the contents
        result = SyncDatabase()
        call_result = native.db_populate_from_bson_file(
            result._rust_db,
            str(path.resolve()).encode("utf-8"),
            native.compression_to_int(compression),
        )

        # Check for errors
        call_result.consume_into_response()
        return result

    @classmethod
    def loads_bson(cls, contents: bytes) -> "SyncDatabase":
        # Load the contents
        result = SyncDatabase()
        call_result = native.db_populate_from_bson_value(
            result._rust_db, native.wrapped_bson.from_bson(bson.decode(contents))
        )

        # Check for errors
        call_result.consume_into_response()
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
        # FIXME: "dump" should really accept a file-like object, not a path!

        if isinstance(path, str):
            path = Path(path)

        if not isinstance(path, Path):
            raise TypeError("The path has to be a Path or a string.")

        if not isinstance(relaxed, bool):
            raise TypeError(relaxed)

        if not isinstance(format, bool):
            raise TypeError(format)

        if not isinstance(n_backups, int):
            raise TypeError(n_backups)

        if n_backups < 0:
            raise ValueError(n_backups)

        call_result = native.db_dump_to_json_file(
            self._rust_db,
            str(path.resolve()).encode("utf-8"),
            relaxed,
            format,
            n_backups,
            native.compression_to_int(compression),
        )
        call_result.consume_into_response()

    def dumps_json(
        self,
        *,
        relaxed: bool,
        format: bool = False,
    ) -> str:
        if not isinstance(relaxed, bool):
            raise TypeError(relaxed)

        if not isinstance(format, bool):
            raise TypeError(format)

        call_result = native.db_dump_to_json_string(self._rust_db, relaxed, format)
        return call_result.consume_into_response()

    def dump_bson(
        self,
        path: Path,
        *,
        n_backups: int = 0,
        compression: Compression = None,
    ) -> None:
        # FIXME: "dump" should really accept a file-like object, not a path!

        if isinstance(path, str):
            path = Path(path)

        if not isinstance(path, Path):
            raise TypeError("The path has to be a Path or a string.")

        if not isinstance(n_backups, int):
            raise TypeError(n_backups)

        if n_backups < 0:
            raise ValueError(n_backups)

        call_result = native.db_dump_to_bson_file(
            self._rust_db,
            str(path.resolve()).encode("utf-8"),
            n_backups,
            native.compression_to_int(compression),
        )
        call_result.consume_into_response()

    def dumps_bson(self) -> bytes:
        call_result = native.db_dump_to_bson_value(
            self._rust_db,
        )
        return bson.encode(call_result.consume_into_response())

    def n_collections(self) -> int:
        call_result = native.db_n_collections(self._rust_db)
        return call_result.consume_into_response()

    def collections(self) -> Iterable["sync_collection.SyncCollection"]:
        call_result = native.db_collection_names(self._rust_db)
        call_result = call_result.consume_into_response()

        for name in call_result:
            yield self.collection(name)

    def collection(self, collection_name: str) -> "sync_collection.SyncCollection":
        if not isinstance(collection_name, str):
            raise TypeError("The collection name has to be a string.")

        return sync_collection.SyncCollection(self, collection_name)

    def drop_collection(self, collection_name: str) -> None:
        if not isinstance(collection_name, str):
            raise TypeError(
                f"The collection name has to be a string, not: {repr(collection_name)}"
            )

        call_result = native.db_drop_collection(
            self._rust_db, collection_name.encode("utf-8")
        )
        call_result.consume_into_response()

    def __getitem__(self, collection_name: str) -> "sync_collection.SyncCollection":
        return self.collection(collection_name)
