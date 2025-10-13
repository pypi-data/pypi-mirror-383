from typing import List, Optional

from bson import BSON

from .typedefs import *


class DeleteResult:
    def __init__(self, n_deleted: int):
        self.n_deleted = n_deleted

    @classmethod
    def decode(cls, raw: BsonLike) -> "DeleteResult":
        return cls(raw["nDeleted"])


class UpdateResult:
    def __init__(
        self,
        matched_count: int,
        modified_count: int,
        upserted_id: Optional[BSON],
    ):
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.upserted_id = upserted_id

    @classmethod
    def decode(cls, raw: BSON) -> "UpdateResult":
        return cls(
            raw["matchedCount"],
            raw["modifiedCount"],
            raw["upsertedId"],
        )


class InsertOneResult:
    def __init__(
        self,
        inserted_id: BSON,
    ):
        self.inserted_id = inserted_id

    @classmethod
    def decode(cls, raw: BSON) -> "InsertOneResult":
        return cls(
            raw["insertedId"],
        )


class InsertManyResult:
    def __init__(
        self,
        inserted_ids: List[BSON],
    ):
        self.inserted_ids = inserted_ids

    @classmethod
    def decode(cls, raw: BSON) -> "InsertManyResult":
        return cls(
            raw["insertedIds"],
        )
