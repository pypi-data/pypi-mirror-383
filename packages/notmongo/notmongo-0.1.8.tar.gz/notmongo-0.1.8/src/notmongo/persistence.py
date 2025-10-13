import time
from pathlib import Path
from typing import Literal, Optional, Union

from . import sync_database
from .typedefs import *


class BasePersistence:
    def __init__(self):
        self.db: Optional["sync_database.SyncDatabase"] = (
            None  # This is set by the database when the persistence is assigned to it
        )

    def save_now(self):
        if self.db is None:
            raise ValueError("Assign the persistence to a database before using it")

    def notify_change(self):
        pass


# TODO: Saves are only triggered on changes to the database. This means that if
# one operation is made, and then a long pause the changes won't be written to
# disk until another change is performed.
class FilePersistence(BasePersistence):
    def __init__(
        self,
        file_path: Union[Path, str],
        *,
        n_backups: int = 3,
        file_format: Literal["json", "bson"] = "json",
        save_interval: float = 60,
        use_relaxed_extjson: bool = False,
        format_json: bool = False,
        compression: Compression = None,
    ):
        super().__init__()

        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not isinstance(file_path, Path):
            raise TypeError(file_path)

        if not isinstance(n_backups, int):
            raise TypeError(n_backups)

        if n_backups < 0:
            raise ValueError("The number of backups cannot be negative.")

        if file_format == "bson" and compression is not None:
            raise ValueError("Compression is not currently supported with BSON files")

        file_format = file_format.lower()  # type: ignore
        if file_format not in ("json", "bson"):
            raise ValueError('The file format needs to be either "json" or "bson"')

        if not isinstance(format_json, bool):
            raise TypeError(format_json)

        self.file_path = file_path
        self.n_backups = n_backups
        self.file_format = file_format
        self.save_interval = save_interval
        self.use_relaxed_extjson = use_relaxed_extjson
        self.format_json = format_json
        self.compression: Compression = compression

        self.is_dirty = False
        self.last_save_time_monotonic = time.monotonic()

    def save_now(self):
        # Is the database even set?
        if self.db is None:
            raise ValueError("Assign the persistence to a database before using it")

        # Save the database
        if self.file_format == "json":
            self.db.dump_json(
                self.file_path,
                relaxed=self.use_relaxed_extjson,
                format=self.format_json,
                n_backups=self.n_backups,
                compression=self.compression,
            )
        else:
            self.db.dump_bson(
                self.file_path,
                n_backups=self.n_backups,
                compression=None,
            )

        # Keep track of this save
        self.is_dirty = False
        self.last_save_time_monotonic = time.monotonic()

    def notify_change(self):
        self.is_dirty = True

        if (
            self.save_interval == 0
            or self.last_save_time_monotonic + self.save_interval < time.monotonic()
        ):
            self.save_now()

    def __del__(self):
        if self.is_dirty:
            self.save_now()
