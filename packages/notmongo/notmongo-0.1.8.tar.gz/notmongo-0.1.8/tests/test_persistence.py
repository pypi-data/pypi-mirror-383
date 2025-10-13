import tempfile
from pathlib import Path

import pytest

import notmongo as nm
from notmongo.typedefs import *

TESTS_DIRECTORY = Path(__file__).resolve().parent
TEST_DB_JSON_PATH = TESTS_DIRECTORY / "test-db.json"


def _load_test_db() -> nm.AsyncDatabase:
    return nm.AsyncDatabase.load_json(TEST_DB_JSON_PATH)


@pytest.mark.asyncio
async def test_file_persistence() -> None:
    # Create a DB
    db = _load_test_db()

    # Set up the persistence
    with tempfile.NamedTemporaryFile() as temp_file:
        file_path = Path(temp_file.name)

    assert file_path.parent.exists()
    assert not file_path.exists()

    db.persistence = nm.FilePersistence(
        file_path,
        n_backups=2,
        file_format="json",
        save_interval=0,
        format_json=False,
    )

    # There shouldn't be a file yet
    assert not file_path.exists(), (
        "The file has been created before any changes to the DB were made"
    )

    # Perform any mutation in the db
    await db["test-collection"].insert_one({"_id": "some-id"})

    # Now there has to be a file
    assert file_path.exists(), "No file was written, despite mutating changes to the DB"
