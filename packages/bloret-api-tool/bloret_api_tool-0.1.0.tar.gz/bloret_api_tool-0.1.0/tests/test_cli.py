"""Tests for the CLI module."""
import pytest
from unittest.mock import patch, Mock
import sys
import json

from bloret_api_tool.cli import main


def test_main_no_args(capsys):
    """Test main function with no arguments."""
    main([])
    captured = capsys.readouterr()
    assert "usage: BLAPI" in captured.out


@patch('bloret_api_tool.cli.Client')
def test_main_get_command(mock_client_class, capsys):
    """Test main function with get command."""
    # Configure the mock
    mock_client_instance = Mock()
    mock_client_instance.request.return_value = {"status": "success"}
    mock_client_class.return_value = mock_client_instance
    
    # Call main with arguments
    test_args = ["get", "/test-endpoint"]
    main(test_args)
    
    # Assertions
    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output == {"status": "success"}
    mock_client_instance.request.assert_called_once_with("GET", "/test-endpoint")


@patch('bloret_api_tool.cli.Client')
def test_main_post_command(mock_client_class, capsys):
    """Test main function with post command."""
    # Configure the mock
    mock_client_instance = Mock()
    mock_client_instance.request.return_value = {"status": "created"}
    mock_client_class.return_value = mock_client_instance
    
    # Call main with arguments
    test_args = ["post", "/test-endpoint", "--data", '{"key": "value"}']
    main(test_args)
    
    # Assertions
    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output == {"status": "created"}
    mock_client_instance.request.assert_called_once_with("POST", "/test-endpoint", {"key": "value"})