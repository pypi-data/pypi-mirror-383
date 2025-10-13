from typing import *  # type: ignore

BsonLike: TypeAlias = Union[
    Dict[str, "BsonLike"], List["BsonLike"], str, int, float, bool, None
]

BsonDoc: TypeAlias = Dict[str, BsonLike]

SortList: TypeAlias = List[Tuple[str, Literal[-1, 1]]]

Compression: TypeAlias = Union[None, Literal["zip"]]


class NotmongoError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __repr__(self):
        return f"<NotMongoException {repr(self.message)}>"
