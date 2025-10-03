from unittest.mock import MagicMock

import pytest

from app.db import Database


@pytest.fixture
def mock_database(mocker):
    mock = mocker.patch("app.db.pymongo.MongoClient")
    return mock

class TestDatabase:

    @staticmethod
    def test_mongo_db_connection_error(
            mock_database: any
    ):
        mock_database.side_effect = Exception("Error to connect")

        with pytest.raises(Exception) as e:
            Database()

        assert str(e.value) == "Error to connect"

    @staticmethod
    def test_mongo_db_connection_close_ok(
            mock_database: any
    ):
        mock_database.return_value = MagicMock()

        db = Database()

        db.close()

        assert db.conn.close.called

    @staticmethod
    def test_mongo_db_returns_none_on_get_collection(
            mock_database: any
    ):
        mock_database.conn = MagicMock()

        db = Database()

        db.conn = None

        col = db.get_collection("test")

        assert col is None