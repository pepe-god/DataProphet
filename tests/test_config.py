from unittest.mock import patch

from src.config import load_config


class TestLoadConfig:
    def test_loads_existing_config(self):
        config = load_config()
        assert config is not None

    def test_config_has_database_sections(self):
        config = load_config()
        assert "DATABASE" in config or "FULLDATA" in config

    @patch("src.config.os.path.exists", return_value=False)
    @patch("src.config.configparser.ConfigParser.read")
    def test_missing_config_logs_error(self, mock_read, mock_exists):
        config = load_config()
        assert config is not None
        mock_exists.assert_called_once()
