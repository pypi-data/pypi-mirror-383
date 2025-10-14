"""
Configuration management module tests
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from scriptmate.config import ConfigManager


class TestConfigManager:
    """Configuration manager tests"""

    def setup_method(self):
        """Setup before tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "config.json"

        # Mock get_config_file to use temp file
        with patch("scriptmate.config.get_config_file", return_value=self.config_file):
            self.config_manager = ConfigManager()

    def test_load_config_empty(self):
        """Test loading empty configuration"""
        config = self.config_manager.load_config()
        assert config is None

    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        test_config = {
            "api_key": "test-key",
            "model_name": "gpt-3.5-turbo",
            "base_url": "https://api.openai.com/v1",
        }

        self.config_manager.save_config(test_config)
        loaded_config = self.config_manager.load_config()

        assert loaded_config["api_key"] == "test-key"
        assert loaded_config["model_name"] == "gpt-3.5-turbo"
        assert loaded_config["base_url"] == "https://api.openai.com/v1"
        assert "updated_at" in loaded_config

    def test_is_configured_false(self):
        """Test unconfigured state"""
        assert not self.config_manager.is_configured()

    def test_is_configured_true(self):
        """Test configured state"""
        test_config = {
            "api_key": "test-key",
            "model_name": "gpt-3.5-turbo",
            "base_url": "https://api.openai.com/v1",
        }

        self.config_manager.save_config(test_config)
        assert self.config_manager.is_configured()

    def test_get_api_config(self):
        """Test getting API configuration"""
        test_config = {
            "api_key": "test-key",
            "model_name": "gpt-3.5-turbo",
            "base_url": "https://api.openai.com/v1",
        }

        self.config_manager.save_config(test_config)
        api_config = self.config_manager.get_api_config()

        assert api_config["api_key"] == "test-key"
        assert api_config["model_name"] == "gpt-3.5-turbo"
        assert api_config["base_url"] == "https://api.openai.com/v1"

    def test_get_api_config_not_found(self):
        """Test getting non-existent API configuration"""
        with pytest.raises(Exception, match="Configuration not found"):
            self.config_manager.get_api_config()
