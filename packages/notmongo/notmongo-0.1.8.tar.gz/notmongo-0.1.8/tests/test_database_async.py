import json
import random
import tempfile
import zipfile
from pathlib import Path
from typing import *  # type: ignore

import bson
import bson.errors
import pytest

import notmongo as nm

TESTS_DIRECTORY = Path(__file__).resolve().parent
TEST_DB_JSON_PATH = TESTS_DIRECTORY / "test-db.json"

COMPRESSIONS = [None, "zip"]


def _load_test_db_dict() -> Dict[str, Any]:
    with open(TEST_DB_JSON_PATH) as f:
        return json.load(f)


async def _verify_loaded_db(db: nm.AsyncDatabase):
    n_documents = {"animals": 3, "homes": 2}

    # Correct number of collections
    assert await db.n_collections() == len(n_documents)

    # Collections have the correct names and number of documents
    async for collection in db.collections():
        assert await collection.count_all_documents() == n_documents[collection.name]


def _as_file(
    contents: Union[bytes, str],
    compression: nm.Compression,
) -> Path:
    # Make sure the contents are bytes
    if isinstance(contents, str):
        contents = contents.encode("utf-8")

    if not isinstance(contents, bytes):
        raise TypeError(contents)

    # Write to a temporary file
    if compression is None:
        f = tempfile.NamedTemporaryFile(mode="wb", delete=False)
        f.write(contents)
        return Path(f.name)

    if compression == "zip":
        # Write to a temporary file
        f = tempfile.NamedTemporaryFile(mode="wb", delete=False)
        with zipfile.ZipFile(f, "w") as zip_file:
            zip_file.writestr(f"some_random_name_{random.random()}.bson", contents)

        return Path(f.name)

    assert False, f"Invalid compression: `{compression}`"


def _read_compressed(path: Path, compression: nm.Compression) -> bytes:
    if compression is None:
        return path.read_bytes()

    if compression == "zip":
        with zipfile.ZipFile(path, "r") as zip_file:
            assert len(zip_file.namelist()) == 1
            return zip_file.read(zip_file.namelist()[0])

    assert False, f"Invalid compression: `{compression}`"


@pytest.mark.asyncio
async def test_handling_db():
    db = nm.AsyncDatabase()
    collection = db.collection("test-collection")
    await collection.insert_one({"key": "value"})
    assert await db.n_collections() == 1

    async for also_collection in db.collections():
        break

    assert collection.name == also_collection.name  # type: ignore

    await collection.drop()
    assert await db.n_collections() == 0


@pytest.mark.asyncio
async def test_loads_valid_bson():
    as_dict = _load_test_db_dict()
    as_bson = bson.encode(as_dict)
    db = nm.AsyncDatabase.loads_bson(as_bson)

    await _verify_loaded_db(db)


@pytest.mark.asyncio
async def test_loads_invalid_bson():
    as_bson = b"1234567890"

    with pytest.raises((nm.NotmongoError, bson.errors.InvalidBSON)):
        nm.AsyncDatabase.loads_bson(as_bson)


@pytest.mark.asyncio
@pytest.mark.parametrize("compression", COMPRESSIONS)
async def test_load_valid_bson(compression: nm.Compression):
    as_dict = _load_test_db_dict()
    as_bson = bson.encode(as_dict)
    as_path = _as_file(as_bson, compression=compression)

    db = nm.AsyncDatabase.load_bson(as_path, compression=compression)

    await _verify_loaded_db(db)


@pytest.mark.asyncio
@pytest.mark.parametrize("compression", COMPRESSIONS)
async def test_load_invalid_bson(compression: nm.Compression):
    as_bson = b"1234567890"
    as_path = _as_file(as_bson, compression=compression)

    with pytest.raises((nm.NotmongoError, bson.errors.InvalidBSON)):
        nm.AsyncDatabase.load_bson(as_path, compression=compression)


@pytest.mark.asyncio
async def test_loads_valid_json():
    as_dict = _load_test_db_dict()
    as_json = json.dumps(as_dict)
    db = nm.AsyncDatabase.loads_json(as_json)

    await _verify_loaded_db(db)


@pytest.mark.asyncio
async def test_loads_invalid_json_string():
    as_json = "{foo?"

    with pytest.raises(nm.NotmongoError):
        nm.AsyncDatabase.loads_json(as_json)


@pytest.mark.asyncio
@pytest.mark.parametrize("compression", COMPRESSIONS)
async def test_load_valid_json(compression: nm.Compression):
    as_dict = _load_test_db_dict()
    as_json = json.dumps(as_dict)
    as_path = _as_file(as_json, compression)

    db = nm.AsyncDatabase.load_json(as_path, compression=compression)

    await _verify_loaded_db(db)


@pytest.mark.asyncio
@pytest.mark.parametrize("compression", COMPRESSIONS)
async def test_load_invalid_json(compression: nm.Compression):
    as_path = _as_file("{foo?", compression)

    with pytest.raises(nm.NotmongoError):
        nm.AsyncDatabase.load_json(as_path, compression=compression)


@pytest.mark.asyncio
async def test_dumps_bson():
    as_dict_orig = _load_test_db_dict()
    as_bson_orig = bson.encode(as_dict_orig)
    db = nm.AsyncDatabase.loads_bson(as_bson_orig)

    as_bson_dump = db.dumps_bson()
    as_dict_dump = bson.decode(as_bson_dump)

    assert as_dict_orig == as_dict_dump


@pytest.mark.asyncio
@pytest.mark.parametrize("compression", COMPRESSIONS)
async def test_dump_bson(compression: nm.Compression):
    as_dict_orig = _load_test_db_dict()
    as_bson_orig = bson.encode(as_dict_orig)
    db = nm.AsyncDatabase.loads_bson(as_bson_orig)

    with tempfile.NamedTemporaryFile() as f:
        temp_path = Path(f.name)

    db.dump_bson(temp_path, compression=compression)
    as_dict_dump = bson.decode(_read_compressed(temp_path, compression))

    assert as_dict_orig == as_dict_dump


@pytest.mark.asyncio
async def test_dumps_json():
    as_dict_orig = _load_test_db_dict()
    as_bson_orig = bson.encode(as_dict_orig)
    db = nm.AsyncDatabase.loads_bson(as_bson_orig)

    as_json_dump = db.dumps_json()
    as_dict_dump = json.loads(as_json_dump)

    assert as_dict_orig == as_dict_dump


@pytest.mark.asyncio
@pytest.mark.parametrize("compression", COMPRESSIONS)
async def test_dump_json(compression: nm.Compression):
    as_dict_orig = _load_test_db_dict()
    as_bson_orig = bson.encode(as_dict_orig)
    db = nm.AsyncDatabase.loads_bson(as_bson_orig)

    with tempfile.NamedTemporaryFile() as f:
        temp_path = Path(f.name)

    db.dump_json(temp_path, compression=compression)
    as_dict_dump = json.loads(_read_compressed(temp_path, compression).decode("utf-8"))

    assert as_dict_orig == as_dict_dump
