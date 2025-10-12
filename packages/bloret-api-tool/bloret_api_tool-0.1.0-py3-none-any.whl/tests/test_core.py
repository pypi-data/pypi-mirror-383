"""Tests for the core module."""
import pytest
import json
from unittest.mock import Mock, patch

from bloret_api_tool.core import Client, request_api


class TestClient:
    """Tests for the Client class."""
    
    def test_init(self):
        """Test Client initialization."""
        client = Client(base_url="https://test.api.com", token="test-token")
        assert client.base_url == "https://test.api.com"
        assert client.token == "test-token"
    
    def test_init_default_url(self):
        """Test Client initialization with default URL."""
        client = Client(token="test-token")
        assert client.base_url == "https://api.bloret.com"
    
    @patch('requests.Session.get')
    def test_get_request(self, mock_get):
        """Test GET request."""
        # Configure the mock
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.content = b'{"status": "success"}'
        mock_get.return_value = mock_response
        
        # Create client and make request
        client = Client(token="test-token")
        result = client.request("GET", "/test-endpoint")
        
        # Assertions
        assert result == {"status": "success"}
        mock_get.assert_called_once()
    
    @patch('requests.Session.post')
    def test_post_request(self, mock_post):
        """Test POST request."""
        # Configure the mock
        mock_response = Mock()
        mock_response.json.return_value = {"status": "created"}
        mock_response.content = b'{"status": "created"}'
        mock_post.return_value = mock_response
        
        # Create client and make request
        client = Client(token="test-token")
        result = client.request("POST", "/test-endpoint", data={"key": "value"})
        
        # Assertions
        assert result == {"status": "created"}
        mock_post.assert_called_once()


def test_request_api():
    """Test the request_api convenience function."""
    with patch('bloret_api_tool.core.Client') as mock_client_class:
        # Configure the mock
        mock_client_instance = Mock()
        mock_client_instance.request.return_value = {"status": "success"}
        mock_client_class.return_value = mock_client_instance
        
        # Call the function
        result = request_api("GET", "/test-endpoint", token="test-token")
        
        # Assertions
        assert result == {"status": "success"}
        mock_client_class.assert_called_once_with(base_url="https://api.bloret.com", token="test-token")
        mock_client_instance.request.assert_called_once_with("GET", "/test-endpoint", None)