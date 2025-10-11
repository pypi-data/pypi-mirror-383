"""
Test cases for the Euno SDK resources functionality.
"""

import pytest
from unittest.mock import patch, Mock
from euno.resources import list_resources_command, _display_csv, _display_pretty
from euno.api import EunoAPIClient


class TestResourcesCommands:
    """Test cases for resources commands."""

    def setup_method(self):
        """Set up test fixtures."""
        pass

    @patch("euno.resources.config")
    @patch("euno.resources.api_client")
    def test_list_resources_command_success(self, mock_api_client, mock_config):
        """Test successful resources list command."""
        mock_config.is_configured.return_value = True
        mock_config.get_token.return_value = "test-token"
        mock_config.get_account_id.return_value = "4"

        mock_response = {
            "resources": [
                {"uri": "test.uri.1", "name": "Test Resource 1", "type": "table"},
                {"uri": "test.uri.2", "name": "Test Resource 2", "type": "view"},
            ],
            "count": 2,
            "relevance_sort": None,
            "warnings": [],
        }
        mock_api_client.search_resources.return_value = mock_response

        with patch("click.echo") as mock_echo:
            list_resources_command(
                eql="has child(true, 1)",
                properties="uri,name,type",
                page=1,
                page_size=10,
                sorting="name",
                relationships="parent,child",
                format="json",
            )

            mock_api_client.search_resources.assert_called_once()
            mock_echo.assert_called()

    @patch("euno.resources.config")
    def test_list_resources_command_not_configured(self, mock_config):
        """Test resources list command when not configured."""
        mock_config.is_configured.return_value = False

        with patch("click.echo") as mock_echo:
            list_resources_command()

            echo_calls = [call[0][0] for call in mock_echo.call_args_list]
            assert any("not configured" in call for call in echo_calls)

    @patch("euno.resources.config")
    def test_list_resources_command_no_account_id(self, mock_config):
        """Test resources list command when no account ID is configured."""
        mock_config.is_configured.return_value = True
        mock_config.get_token.return_value = "test-token"
        mock_config.get_account_id.return_value = None

        with patch("click.echo") as mock_echo:
            list_resources_command()

            echo_calls = [call[0][0] for call in mock_echo.call_args_list]
            assert any("No account ID configured" in call for call in echo_calls)

    def test_display_csv_with_properties(self):
        """Test CSV display formatting with specified properties."""
        response = {
            "resources": [
                {"uri": "test.uri.1", "name": "Test Resource 1", "type": "table"},
                {"uri": "test.uri.2", "name": "Test Resource 2", "type": "view"},
            ],
            "count": 2,
        }

        with patch("click.echo") as mock_echo:
            _display_csv(response, ["uri", "name", "type"])

            # Check that CSV output was generated with correct order
            mock_echo.assert_called()
            csv_output = mock_echo.call_args[0][0]
            assert "uri,name,type" in csv_output
            assert "test.uri.1,Test Resource 1,table" in csv_output

    def test_display_csv_default_properties(self):
        """Test CSV display formatting with default properties."""
        response = {
            "resources": [
                {"uri": "test.uri.1", "name": "Test Resource 1", "type": "table"},
                {"uri": "test.uri.2", "name": "Test Resource 2", "type": "view"},
            ],
            "count": 2,
        }

        with patch("click.echo") as mock_echo:
            _display_csv(response, ["uri", "type", "name"])  # Default properties

            # Check that CSV output was generated with default order
            mock_echo.assert_called()
            csv_output = mock_echo.call_args[0][0]
            assert "uri,type,name" in csv_output  # Default order
            assert "test.uri.1" in csv_output
            assert "Test Resource 1" in csv_output

    def test_display_pretty(self):
        """Test pretty table display formatting."""
        response = {
            "resources": [
                {"uri": "test.uri.1", "name": "Test Resource 1", "type": "table"},
                {"uri": "test.uri.2", "name": "Test Resource 2", "type": "view"},
            ],
            "count": 2,
        }

        with patch("click.echo") as mock_echo:
            _display_pretty(response)

            # Check that pretty output was generated
            assert mock_echo.call_count > 0
            # Get all the echo calls
            calls = mock_echo.call_args_list
            output_text = " ".join([call[0][0] for call in calls if call[0]])
            assert "Found 2 resources" in output_text


class TestEunoAPIClientResources:
    """Test cases for API client resources functionality."""

    def test_search_resources_success(self):
        """Test successful resources search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "resources": [{"uri": "test.uri", "name": "Test", "type": "table"}],
            "count": 1,
        }
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session.get", return_value=mock_response):
            client = EunoAPIClient()
            result = client.search_resources("test-token", "4", {"page": 1, "page_size": 10})

            assert result["count"] == 1
            assert len(result["resources"]) == 1
            assert result["resources"][0]["uri"] == "test.uri"

    def test_search_resources_failure(self):
        """Test resources search failure."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")

        with patch("requests.Session.get", return_value=mock_response):
            client = EunoAPIClient()

            with pytest.raises(Exception):
                client.search_resources("invalid-token", "4", {"page": 1})
