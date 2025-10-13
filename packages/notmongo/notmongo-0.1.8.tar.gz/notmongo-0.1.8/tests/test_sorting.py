import random
from pathlib import Path
from typing import Iterable

import notmongo as nm
from notmongo.typedefs import *

TESTS_DIRECTORY = Path(__file__).resolve().parent
TEST_DB_JSON_PATH = TESTS_DIRECTORY / "test-db.json"


def _verify_sorting(documents: Iterable[BsonLike], sort: SortList):
    """
    Makes sure that documents are sorted in the expected order. The documents
    are inserted into an empty collection, and queried with the given sort. If
    any documents are not returned in the same order as they were passed to this
    function an AssertionError is raised.
    """

    # Randomize the document order, so they aren't sorted correctly merely by
    # accident. Make sure to do this deterministically so the test results are
    # reproducible.
    documents = list(documents)
    shuffled_documents = documents.copy()
    random.Random(0).shuffle(shuffled_documents)

    # If shuffling randomly led to a correct order, reverse their order
    if documents == shuffled_documents:
        shuffled_documents.reverse()

    # Insert the documents into an empty database
    db = nm.SyncDatabase()
    col = db.collection("sorting-test")
    col.insert_many(shuffled_documents)

    # Query the documents with the given sort
    query_result = col.find(sort=sort, projection={"_id": False})
    query_result = list(query_result)

    # assert id_order_should == id_order_got
    assert documents == query_result


def test_single_field_name():
    _verify_sorting(
        [
            {"value": "bird"},
            {"value": "cat"},
            {"value": "dog"},
            {"value": "eel"},
        ],
        "value",
    )


def test_string():
    _verify_sorting(
        [
            {"value": "bird"},
            {"value": "cat"},
            {"value": "dog"},
            {"value": "eel"},
        ],
        [("value", 1)],
    )


def test_numeric_descending():
    _verify_sorting(
        [
            {"value": 4},
            {"value": 3},
            {"value": 2},
            {"value": 1},
        ],
        [("value", -1)],
    )


def test_different_numeric_types():
    _verify_sorting(
        [
            {"value": -2},
            {"value": -1.5},
            {"value": -1},
            {"value": False},
            {"value": True},
            {"value": 2},
            {"value": 2.5},
            {"value": 2**40},  # Doesn't fit into a 32-Bit Integer
            {"value": 2**60},  # Oudside of a Double's continuous integer range
        ],
        [("value", 1)],
    )


def test_multiple():
    _verify_sorting(
        [
            {"b1": 0, "b2": 0, "b3": 0},
            {"b1": 0, "b2": 0, "b3": 1},
            {"b1": 0, "b2": 1, "b3": 0},
            {"b1": 0, "b2": 1, "b3": 1},
            {"b1": 1, "b2": 0, "b3": 0},
            {"b1": 1, "b2": 0, "b3": 1},
            {"b1": 1, "b2": 1, "b3": 0},
            {"b1": 1, "b2": 1, "b3": 1},
        ],
        [("b1", 1), ("b2", 1), ("b3", 1)],
    )


# TODO:
# - Other sortables:
#   - DateTime
#   - Binary (important for uuids!)
#   - ObjectId
#   - Boolean
# - Special cases
#   - arrays
# - connect to actual mongodb and compare the orders? Maybe even fuzz?
