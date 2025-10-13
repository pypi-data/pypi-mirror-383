from pathlib import Path
from typing import AsyncIterable, Iterable

import pytest

import notmongo as nm
from notmongo.typedefs import *

TESTS_DIRECTORY = Path(__file__).resolve().parent
TEST_DB_JSON_PATH = TESTS_DIRECTORY / "test-db.json"


def _load_test_db() -> nm.AsyncDatabase:
    return nm.AsyncDatabase.load_json(TEST_DB_JSON_PATH)


def _load_test_collection() -> nm.AsyncCollection:
    return _load_test_db().collection("animals")


async def _collect_async_generator(generator: AsyncIterable[Any]) -> List[Any]:
    result = []

    async for value in generator:
        result.append(value)

    return result


async def _verify_result_ids(
    documents: Union[nm.AsyncCollection, Iterable[BsonLike]],
    expected_ids: Iterable[BsonLike],
):
    # Get all ids
    if isinstance(documents, nm.AsyncCollection):
        documents = await _collect_async_generator(documents.find({}))

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


@pytest.mark.asyncio
async def test_count_all_documents():
    col = _load_test_collection()
    assert await col.count_all_documents() == 3


@pytest.mark.asyncio
async def test_count_documents_all():
    col = _load_test_collection()
    assert await col.count_documents({}) == 3


@pytest.mark.asyncio
async def test_count_documents_one_attriubute():
    col = _load_test_collection()
    assert await col.count_documents({"canSwim": True}) == 2


@pytest.mark.asyncio
async def test_count_documents_two_attriubutes():
    col = _load_test_collection()
    assert await col.count_documents({"canSwim": True, "legs": 4}) == 1


@pytest.mark.asyncio
async def test_delete_many_no_filter():
    col = _load_test_collection()
    await col.delete_many({})
    await _verify_result_ids(col, set())


@pytest.mark.asyncio
async def test_delete_many_with_filter():
    col = _load_test_collection()
    await col.delete_many({"legs": 4})
    await _verify_result_ids(col, {"id-1-fish"})


@pytest.mark.asyncio
async def test_delete_one_no_filter():
    col = _load_test_collection()
    await col.delete_one({})
    assert await col.count_all_documents() == 2


@pytest.mark.asyncio
async def test_find_all():
    col = _load_test_collection()
    results = await _collect_async_generator(col.find({}))
    await _verify_result_ids(results, {"id-1-cat", "id-1-dog", "id-1-fish"})


@pytest.mark.asyncio
async def test_find_all_skip_1():
    col = _load_test_collection()
    results = await _collect_async_generator(col.find({}, skip=1))
    results = list(results)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_find_all_limit_1():
    col = _load_test_collection()
    results = await _collect_async_generator(col.find({}, limit=1))
    results = list(results)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_find_all_with_sort():
    col = _load_test_collection()
    results = await _collect_async_generator(col.find({}, sort=[("age", -1)]))
    results = list(results)

    assert len(results) == 3
    assert results[0]["_id"] == "id-1-dog"
    assert results[1]["_id"] == "id-1-cat"
    assert results[2]["_id"] == "id-1-fish"


@pytest.mark.asyncio
async def test_find_all_with_sort_and_skip():
    col = _load_test_collection()
    results = await _collect_async_generator(col.find({}, sort=[("age", -1)], skip=2))

    assert len(results) == 1
    assert results[0]["_id"] == "id-1-fish"


@pytest.mark.asyncio
async def test_find_all_with_sort_and_limit():
    col = _load_test_collection()
    results = await _collect_async_generator(col.find({}, sort=[("age", -1)], limit=2))

    assert len(results) == 2
    assert results[0]["_id"] == "id-1-dog"
    assert results[1]["_id"] == "id-1-cat"


@pytest.mark.asyncio
async def test_find_all_with_sort_and_skip_and_limit():
    col = _load_test_collection()
    results = await _collect_async_generator(
        col.find({}, sort=[("age", -1)], skip=1, limit=1)
    )

    assert len(results) == 1
    assert results[0]["_id"] == "id-1-cat"


@pytest.mark.asyncio
async def test_find_all_skip_some():
    col = _load_test_collection()
    results = await _collect_async_generator(col.find({}, skip=2))
    assert len(results) == 1


@pytest.mark.asyncio
async def test_find_all_skip_all():
    col = _load_test_collection()
    results = await _collect_async_generator(col.find({}, skip=3))
    assert len(results) == 0


@pytest.mark.asyncio
async def test_find_one_any():
    col = _load_test_collection()
    result = await col.find_one({})

    assert result is not None


@pytest.mark.asyncio
async def test_find_one_with_filter():
    col = _load_test_collection()
    result = await col.find_one({"_id": "id-1-dog"})

    assert result is not None
    assert result["_id"] == "id-1-dog"


@pytest.mark.asyncio
async def test_find_one_with_sort():
    col = _load_test_collection()
    result = await col.find_one({}, sort=[("age", -1)])

    assert result is not None
    assert result["_id"] == "id-1-dog"


@pytest.mark.asyncio
async def test_find_one_with_sort_and_skip():
    col = _load_test_collection()
    result = await col.find_one({}, sort=[("age", -1)], skip=2)

    assert result is not None
    assert result["_id"] == "id-1-fish"


@pytest.mark.asyncio
async def test_insert_one():
    col = _load_test_collection()
    result = await col.insert_one({"_id": "id-new-document", "canSwim": True})

    assert result.inserted_id == "id-new-document"
    await _verify_result_ids(
        col, {"id-1-cat", "id-1-dog", "id-1-fish", "id-new-document"}
    )


@pytest.mark.asyncio
async def test_insert_one_without_id():
    col = _load_test_collection()

    result = await col.insert_one({"canSwim": True})

    await _verify_result_ids(
        col, {"id-1-cat", "id-1-dog", "id-1-fish", result.inserted_id}
    )


@pytest.mark.asyncio
async def test_insert_many():
    col = _load_test_collection()
    result = await col.insert_many(
        [
            {"_id": "id-new-document-1", "canSwim": True},
            {"_id": "id-new-document-2", "canSwim": True},
        ]
    )

    assert list(result.inserted_ids) == ["id-new-document-1", "id-new-document-2"]

    await _verify_result_ids(
        col,
        {"id-1-cat", "id-1-dog", "id-1-fish", "id-new-document-1", "id-new-document-2"},
    )


@pytest.mark.asyncio
async def test_insert_many_without_ids():
    col = _load_test_collection()
    result = await col.insert_many(
        [
            {"_id": "id-new-document-1", "canSwim": True},
            {"_id": "id-new-document-2", "canSwim": True},
        ]
    )
    await _verify_result_ids(
        col,
        {"id-1-cat", "id-1-dog", "id-1-fish"} | set(result.inserted_ids),
    )


@pytest.mark.asyncio
async def test_replace_one_with_match():
    col = _load_test_collection()
    await col.replace_one(
        {"_id": "id-1-fish"},
        {"_id": "id-new-document"},
        upsert=False,
    )
    await _verify_result_ids(col, {"id-1-cat", "id-1-dog", "id-new-document"})


@pytest.mark.asyncio
async def test_replace_one_without_match():
    col = _load_test_collection()
    await col.replace_one(
        {"_id": "id-nonexistent"},
        {"_id": "id-new-document"},
        upsert=False,
    )
    await _verify_result_ids(col, {"id-1-cat", "id-1-dog", "id-1-fish"})


@pytest.mark.asyncio
async def test_replace_one_without_match_but_upsert():
    col = _load_test_collection()
    await col.replace_one(
        {"_id": "id-nonexistent"},
        {"_id": "id-new-document"},
        upsert=True,
    )
    await _verify_result_ids(
        col, {"id-1-cat", "id-1-dog", "id-1-fish", "id-new-document"}
    )


@pytest.mark.asyncio
async def test_update_one_with_match():
    col = _load_test_collection()
    await col.update_one(
        {"_id": "id-1-fish"},
        {"$set": {"_id": "id-updated-document"}},
        upsert=False,
    )
    await _verify_result_ids(col, {"id-1-cat", "id-1-dog", "id-updated-document"})


@pytest.mark.asyncio
async def test_update_one_without_match():
    col = _load_test_collection()
    await col.update_one(
        {"_id": "id-nonexistent"},
        {"$set": {"_id": "id-updated-document"}},
        upsert=False,
    )
    await _verify_result_ids(col, {"id-1-cat", "id-1-dog", "id-1-fish"})


@pytest.mark.asyncio
async def test_update_one_without_match_but_upsert():
    col = _load_test_collection()
    await col.update_one(
        {"_id": "id-nonexistent"},
        {"$set": {"_id": "id-upserted-document"}},
        upsert=True,
    )
    await _verify_result_ids(
        col, {"id-1-cat", "id-1-dog", "id-1-fish", "id-upserted-document"}
    )


@pytest.mark.asyncio
async def test_update_many_with_match():
    col = _load_test_collection()
    update_result = await col.update_many(
        {"legs": 4},
        {"$set": {"legs": "updated"}, "$unset": "canSwim"},
        upsert=False,
    )

    assert update_result.matched_count == 2
    assert update_result.modified_count == 2
    assert update_result.upserted_id is None

    async for result in col.find():
        if result["_id"] == "id-1-fish":
            assert "canSwim" in result
        else:
            assert result["legs"] == "updated"
            assert "canSwim" not in result


@pytest.mark.asyncio
async def test_update_many_unset_nonexistent_field():
    col = _load_test_collection()
    update_result = await col.update_many(
        {"legs": 4},
        {"$unset": "noSuchField"},
        upsert=False,
    )

    assert update_result.matched_count == 2
    assert update_result.modified_count == 2
    assert update_result.upserted_id is None


@pytest.mark.asyncio
async def test_update_many_without_match():
    col = _load_test_collection()
    update_result = await col.update_many(
        {"legs": 5},
        {"$set": {"legs": "updated"}},
        upsert=False,
    )

    assert update_result.matched_count == 0
    assert update_result.modified_count == 0
    assert update_result.upserted_id is None

    async for result in col.find():
        if result["_id"] == "id-1-fish":
            assert "canSwim" in result
        else:
            assert result["legs"] == 4
            assert "canSwim" in result


@pytest.mark.asyncio
async def test_update_many_without_match_but_upsert():
    col = _load_test_collection()
    update_result = await col.update_many(
        {"_id": "id-nonexistent"},
        {"$set": {"_id": "id-upserted-document"}},
        upsert=True,
    )

    assert update_result.matched_count == 0
    assert update_result.modified_count == 1
    assert update_result.upserted_id is not None

    await _verify_result_ids(
        col, {"id-1-cat", "id-1-dog", "id-1-fish", "id-upserted-document"}
    )

    async for result in col.find():
        if result["_id"] == "id-1-fish":
            assert "canSwim" in result
        elif result["_id"] == "id-upserted-document":
            assert len(result) == 1
        else:
            assert result["legs"] == 4
            assert "canSwim" in result
