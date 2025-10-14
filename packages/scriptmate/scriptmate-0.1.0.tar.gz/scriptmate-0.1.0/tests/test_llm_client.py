"""
LLM client tests
"""

import pytest
import json
from unittest.mock import Mock, patch

from scriptmate.llm_client import LLMClient


class TestLLMClient:
    """LLM client tests"""

    def setup_method(self):
        """Setup before tests"""
        self.client = LLMClient(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
        )

    def test_init(self):
        """Test initialization"""
        assert self.client.api_key == "test-key"
        assert self.client.model_name == "gpt-3.5-turbo"
        assert self.client.base_url == "https://api.openai.com/v1"
        assert "Authorization" in self.client.session.headers

    def test_get_system_prompt(self):
        """Test getting system prompt"""
        prompt = self.client.get_system_prompt()

        assert "Shell command" in prompt
        assert "JSON format" in prompt
        assert "cmd" in prompt
        assert "reason" in prompt

    @patch("scriptmate.llm_client.requests.Session.post")
    def test_generate_command_success(self, mock_post):
        """Test successful command generation"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "cmd": "ls -la",
                                "reason": "List detailed information of current directory",
                            }
                        )
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        result = self.client.generate_command("Show current directory files")

        assert result["cmd"] == "ls -la"
        assert result["reason"] == "List detailed information of current directory"

    @patch("scriptmate.llm_client.requests.Session.post")
    def test_generate_command_api_error(self, mock_post):
        """Test API error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="API request failed"):
            self.client.generate_command("test")

    @patch("scriptmate.llm_client.requests.Session.post")
    def test_generate_command_invalid_json(self, mock_post):
        """Test invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is not valid JSON"}}]
        }
        mock_post.return_value = mock_response

        result = self.client.generate_command("test")

        # Should have fallback handling
        assert "cmd" in result
        assert "reason" in result

    def test_extract_from_text(self):
        """Test extracting command from text"""
        text = "You can use ls -la command to view file details"
        result = self.client._extract_from_text(text)

        assert "cmd" in result
        assert "reason" in result
