"""
API client for communicating with the Euno backend.

This module handles HTTP requests to the Euno API endpoints.
"""

import requests
from typing import Dict, Any, Optional
from .config import config


class EunoAPIClient:
    """Client for making requests to the Euno API."""

    def __init__(self, backend_url: Optional[str] = None):
        self.backend_url = backend_url or config.get_backend_url()
        self.session = requests.Session()

    def _get_headers(self, token: str) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "euno-sdk/0.2.0",
        }

    def search_resources(self, token: str, account_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search resources in the Euno data model.

        Args:
            token (str): The Euno API token.
            account_id (str): The account ID to search in.
            params (Dict[str, Any]): Search parameters including eql, properties,
                pagination, etc.

        Returns:
            Dict[str, Any]: Search results with resources and count.

        Raises:
            requests.exceptions.HTTPError: If the token is invalid or an API error
                occurs.
        """
        headers = self._get_headers(token)
        response = self.session.get(
            f"{self.backend_url}/accounts/{account_id}/data_model/search",
            headers=headers,
            params=params,
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # type: ignore

    def get_account_permissions(self, token: str, account_id: str) -> Dict[str, Any]:
        """
        Get account permissions for the given account ID.

        Args:
            token (str): The Euno API token.
            account_id (str): The account ID to check permissions for.

        Returns:
            Dict[str, Any]: Account permissions information.

        Raises:
            requests.exceptions.HTTPError: If the token is invalid or an API error
                occurs.
        """
        headers = self._get_headers(token)
        response = self.session.get(f"{self.backend_url}/accounts/{account_id}/permissions", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # type: ignore

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a token by making a request to the /user endpoint.

        Args:
            token: The API token to validate

        Returns:
            User information if token is valid

        Raises:
            requests.HTTPError: If the token is invalid or request fails
        """
        url = f"{self.backend_url}/user"
        headers = self._get_headers(token)

        response = self.session.get(url, headers=headers)
        response.raise_for_status()

        return response.json()  # type: ignore

    def get_user(self, token: str) -> Dict[str, Any]:
        """
        Get current user information.

        Args:
            token: The API token

        Returns:
            User information

        Raises:
            requests.HTTPError: If the request fails
        """
        return self.validate_token(token)


# Global API client instance
api_client = EunoAPIClient()
