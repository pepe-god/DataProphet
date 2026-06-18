from unittest.mock import MagicMock, patch

from src.database import DatabaseProvider


class TestDatabaseProvider:
    def setup_method(self):
        DatabaseProvider._pools.clear()
        DatabaseProvider._config = None

    def test_get_pool_returns_none_for_missing_section(self):
        result = DatabaseProvider.get_pool("NONEXISTENT_SECTION")
        assert result is None

    @patch("src.database.load_config")
    @patch("mysql.connector.pooling.MySQLConnectionPool")
    def test_get_pool_creates_pool(self, mock_pool_class, mock_config):
        mock_config.return_value = {"TEST_DB": {"host": "localhost", "user": "root"}}
        mock_pool_class.return_value = MagicMock()
        result = DatabaseProvider.get_pool("TEST_DB")
        assert result is not None
        assert "TEST_DB" in DatabaseProvider._pools

    @patch("src.database.load_config")
    @patch("mysql.connector.pooling.MySQLConnectionPool")
    def test_get_pool_reuses_existing(self, mock_pool_class, mock_config):
        mock_config.return_value = {"TEST_DB": {"host": "localhost"}}
        mock_pool_class.return_value = MagicMock()
        pool1 = DatabaseProvider.get_pool("TEST_DB")
        pool2 = DatabaseProvider.get_pool("TEST_DB")
        assert pool1 is pool2
        mock_pool_class.assert_called_once()

    @patch("src.database.DatabaseProvider.get_pool")
    def test_get_connection_returns_connection(self, mock_get_pool):
        mock_pool = MagicMock()
        mock_pool.get_connection.return_value = "fake_connection"
        mock_get_pool.return_value = mock_pool
        result = DatabaseProvider.get_connection("TEST_DB")
        assert result == "fake_connection"

    @patch("src.database.DatabaseProvider.get_pool", return_value=None)
    def test_get_connection_returns_none_when_no_pool(self, mock_get_pool):
        result = DatabaseProvider.get_connection("NONEXISTENT")
        assert result is None

    @patch("src.database.load_config")
    @patch("mysql.connector.pooling.MySQLConnectionPool", side_effect=Exception("Pool error"))
    def test_get_pool_returns_none_on_error(self, mock_pool_class, mock_config):
        mock_config.return_value = {"TEST_DB": {"host": "localhost"}}
        result = DatabaseProvider.get_pool("TEST_DB")
        assert result is None
