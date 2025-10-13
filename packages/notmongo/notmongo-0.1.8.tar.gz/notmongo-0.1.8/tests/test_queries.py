import sys
from pathlib import Path

TESTS_DIRECTORY = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIRECTORY.parent
TEST_DB_JSON_PATH = TESTS_DIRECTORY / "test-db.json"

sys.path.append(str(PROJECT_ROOT))

from typing import Iterable

import notmongo as nm
from notmongo.typedefs import *

# TODO:
#   - test operators on different datatypes: string < string, id, ...
#   - test field.names.with.dots
#   - read the mongodb operator docs and test edge cases


def _make_collection(documents: Iterable[BsonDoc]) -> nm.SyncCollection:
    db = nm.SyncDatabase()
    col = db.collection("test-advanced-query-collection")
    col.insert_many(documents)
    return col


def _load_test_collection(collection_name: str = "animals") -> nm.SyncCollection:
    db = nm.SyncDatabase.load_json(TEST_DB_JSON_PATH)
    return db.collection(collection_name)


def _verify_result_ids(
    documents: Union[nm.SyncCollection, Iterable[BsonLike]],
    expected_ids: Iterable[BsonLike],
):
    # Get all ids
    if isinstance(documents, nm.SyncCollection):
        documents = documents.find({})

    have_ids = {doc["_id"] for doc in documents}

    expected_ids = set(expected_ids)

    # Superfluous
    superfluous_ids = have_ids - expected_ids
    assert not superfluous_ids, (
        f"Superfluous result items, with these ids: `{'`, `'.join(map(str, superfluous_ids))}`"
    )

    # Missing
    missing_ids = expected_ids - have_ids
    assert not missing_ids, (
        f"Missing result items, with these ids: `{'`, `'.join(map(str, missing_ids))}`"
    )


def _verify_comparison_operator(
    query: Any, values_in_result: Iterable[Any], values_not_in_result: Iterable[Any]
):
    values_in_result = list(values_in_result)
    values_not_in_result = list(values_not_in_result)

    # Insert the values into a new collection
    col = _make_collection(
        [{"testField": val} for val in values_in_result + values_not_in_result]
    )

    # Apply the queries
    result = col.find(query)
    result = list(result)

    # Compare
    values_returned = [val["testField"] for val in result]
    values_returned.sort()
    values_in_result.sort()
    assert values_returned == values_in_result


def test_operator_and_empty():
    col = _load_test_collection()
    result = col.find({"$and": []})
    _verify_result_ids(result, {"id-1-cat", "id-1-dog", "id-1-fish"})


def test_operator_and():
    col = _load_test_collection()
    result = col.find(
        {
            "$and": [
                {"canSwim": True},
                {"age": {"$gt": 2}},
            ]
        }
    )
    _verify_result_ids(result, {"id-1-dog"})


def test_operator_or():
    col = _load_test_collection()
    result = col.find(
        {
            "$or": [
                {"_id": "id-1-cat"},
                {"_id": "id-1-dog"},
            ]
        }
    )
    _verify_result_ids(result, {"id-1-cat", "id-1-dog"})


def test_operator_or_empty():
    col = _load_test_collection()
    result = col.find({"$or": []})
    _verify_result_ids(result, {})


def test_operator_lt_numeric():
    _verify_comparison_operator(
        {"testField": {"$lt": 3}},
        [1, 2],
        [3, 4, 5],
    )


def test_operator_lte_numeric():
    _verify_comparison_operator(
        {"testField": {"$lte": 3}},
        [1, 2, 3],
        [4, 5],
    )


def test_operator_eq_numeric():
    _verify_comparison_operator(
        {"testField": {"$eq": 3}},
        [3],
        [1, 2, 4, 5],
    )


def test_operator_ne_numeric():
    _verify_comparison_operator(
        {"testField": {"$ne": 3}},
        [1, 2, 4, 5],
        [3],
    )


def test_operator_gte_numeric():
    _verify_comparison_operator(
        {"testField": {"$gte": 3}},
        [3, 4, 5],
        [1, 2],
    )


def test_operator_gt_numeric():
    _verify_comparison_operator(
        {"testField": {"$gt": 3}},
        [4, 5],
        [1, 2, 3],
    )


def test_operator_not():
    col = _load_test_collection()
    result = col.find({"$not": {"_id": "id-1-cat"}})
    _verify_result_ids(result, {"id-1-dog", "id-1-fish"})


def test_operator_exists_positive():
    col = _load_test_collection()
    result = col.find({"onlyLandwalkerField": {"$exists": True}})
    _verify_result_ids(result, {"id-1-cat", "id-1-dog"})


def test_operator_exists_negative():
    col = _load_test_collection()
    result = col.find({"onlyLandwalkerField": {"$exists": False}})
    _verify_result_ids(result, {"id-1-fish"})


def test_operator_implicit_eq_scalar_with_array():
    col = _load_test_collection("homes")
    result = col.find({"entrances": "front"})
    _verify_result_ids(result, {"id-2-doghouse"})


def test_operator_explicit_eq_scalar_with_array():
    col = _load_test_collection("homes")
    result = col.find({"entrances": {"$eq": "front"}})
    _verify_result_ids(result, {"id-2-doghouse"})


def test_operator_ne_scalar_with_array():
    col = _load_test_collection("homes")
    result = col.find({"entrances": {"$ne": "front"}})
    _verify_result_ids(result, {"id-2-aquarium"})
