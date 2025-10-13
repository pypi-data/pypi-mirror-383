from pathlib import Path
from typing import Iterable

import pytest

import notmongo as nm
from notmongo.typedefs import *

TESTS_DIRECTORY = Path(__file__).resolve().parent
TEST_DB_JSON_PATH = TESTS_DIRECTORY / "test-db.json"


def _verify_projection(document: BsonLike, projection, expected_fields: Iterable[str]):
    """
    Verifies that projections work as expected, by inserting a document into a
    empy database, querying it, and making sure exactly the correct fields are
    present.
    """

    # Insert the documents int an empty database
    db = nm.SyncDatabase()
    col = db.collection("projection-test")
    col.insert_one(document)

    # Query the document with the given projection
    query_result = col.find(projection=projection)
    query_result = list(query_result)
    assert len(query_result) == 1
    query_result = query_result[0]

    # Prepare some values for easy checking
    expected_fields = set(expected_fields)
    have_fields = set(query_result.keys())

    # Superfluous
    superfluous_fields = have_fields - expected_fields
    assert not superfluous_fields, (
        f"Superfluous fields in the result: `{'`, `'.join(map(str, superfluous_fields))}`"
    )

    # Missing
    missing_fields = expected_fields - have_fields
    assert not missing_fields, (
        f"Missing fields in the result: `{'`, `'.join(map(str, missing_fields))}`"
    )


def test_keep_all_fields_implicit():
    _verify_projection(
        {"_id": None, "a": None, "b": None},
        {},
        {"_id", "a", "b"},
    )


def test_keep_all_fields_explicit():
    _verify_projection(
        {"_id": None, "a": None, "b": None},
        {"_id": True, "a": True, "b": True},
        {"_id", "a", "b"},
    )


def test_drop_all_fields():
    _verify_projection(
        {"_id": None, "a": None, "b": None},
        {"_id": False, "a": False, "b": False},
        {},
    )


def test_keep_some_rest_implicit():
    _verify_projection(
        {"_id": None, "a": None, "b": None},
        {"_id": True, "a": True},
        {"_id", "a"},
    )


def test_drop_some_rest_implicit():
    _verify_projection(
        {"_id": None, "a": None, "b": None},
        {"_id": False, "a": False},
        {"b"},
    )


def test_keep_some_implicit_id():
    _verify_projection(
        {"_id": None, "a": None, "b": None},
        {"a": True},
        {"_id", "a"},
    )


def test_drop_some_implicit_id():
    _verify_projection(
        {"_id": None, "a": None, "b": None},
        {"a": False},
        {"_id", "b"},
    )


def test_invalid_projection():
    with pytest.raises(nm.NotmongoError):
        _verify_projection(
            {"_id": None, "a": None, "b": None},
            {"a": False, "b": True},  # Some fields are true, some false
            {"_id", "b"},
        )
