"""
Authentication strategies for SensorThings API client.
Supports multiple authentication methods using the strategy pattern.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class FrostAuth(ABC):
    """Base authentication strategy interface."""

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        """Return headers for HTTP requests."""
        pass

    @abstractmethod
    def handle_auth_error(self, response: requests.Response) -> None:
        """Handle authentication errors. Override to implement retry logic."""
        pass


class NoAuth(FrostAuth):
    """No authentication strategy - returns empty headers."""

    def get_headers(self) -> dict[str, str]:
        return {}

    def handle_auth_error(self, response: requests.Response) -> None:
        """No special handling for auth errors when no auth is configured."""
        pass


class BasicAuth(FrostAuth):
    """HTTP Basic Authentication strategy."""

    def __init__(self, username: str, password: str):
        """
        Initialize Basic Auth.

        Args:
            username: Username for authentication
            password: Password for authentication
        """
        self.username = username
        self.password = password
        self._auth_tuple = (username, password)

    def get_headers(self) -> dict[str, str]:
        """Return empty headers - Basic auth is handled by requests.Session.auth."""
        return {}

    def get_auth_tuple(self) -> tuple:
        """Return auth tuple for requests.Session.auth."""
        return self._auth_tuple

    def handle_auth_error(self, response: requests.Response) -> None:
        """No special handling for auth errors with basic auth."""
        pass


class TokenAuth(FrostAuth):
    """Bearer token authentication strategy."""

    def __init__(self, token: str):
        """
        Initialize Token Auth.

        Args:
            token: Bearer token for authentication
        """
        self.token = token

    def get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def handle_auth_error(self, response: requests.Response) -> None:
        """No special handling for auth errors with token auth."""
        pass


class KeycloakAuth(FrostAuth):
    """Keycloak OIDC authentication using Resource Owner Password Credentials grant."""

    def __init__(
        self,
        server_url: str,
        realm: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
    ):
        """
        Initialize Keycloak Auth.

        Args:
            server_url: Keycloak server URL (e.g., "https://keycloak.example.com")
            realm: Keycloak realm name
            client_id: Client ID
            client_secret: Client secret
            username: Username for authentication
            password: Password for authentication
        """
        self.server_url = server_url.rstrip("/")
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

        self.token_url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token"

        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0
        self.refresh_token: Optional[str] = None

    def get_headers(self) -> dict[str, str]:
        """Return headers with current access token, fetching new token if needed."""
        if not self.access_token or self._token_expired():
            logger.info("Access token missing or expired, fetching new token from Keycloak")
            self._fetch_token()
        else:
            logger.debug("Using existing access token")

        return {"Authorization": f"Bearer {self.access_token}"}

    def _token_expired(self) -> bool:
        """Check if the current token is expired (with 30 second buffer)."""
        return time.time() >= (self.token_expires_at - 30)

    def _fetch_token(self) -> None:
        """Fetch a new access token from Keycloak."""
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
            "scope": "openid",
        }

        try:
            logger.debug(f"Fetching token from Keycloak: {self.token_url}")
            response = requests.post(self.token_url, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")

            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
            self.token_expires_at = time.time() + expires_in

            logger.info(f"Successfully obtained Keycloak token (expires in {expires_in} seconds)")

        except requests.RequestException as e:
            logger.error(f"Failed to fetch Keycloak token: {e}")
            raise AuthenticationError(f"Keycloak authentication failed: {e}") from e

    def handle_auth_error(self, response: requests.Response) -> None:
        """Handle authentication errors by attempting to refresh the token."""
        if response.status_code in (401, 403):
            logger.warning("Authentication failed, attempting to refresh token")
            self.access_token = None  # Force token refresh on next request
            self.token_expires_at = 0


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""

    pass


def create_auth_strategy(auth_config: dict) -> FrostAuth:
    """
    Factory function to create authentication strategy from configuration.

    Args:
        auth_config: Authentication configuration dictionary

    Returns:
        Appropriate authentication strategy instance

    Raises:
        ValueError: If auth method is unknown or configuration is invalid
    """
    if not auth_config:
        return NoAuth()

    auth_method = auth_config.get("method", "none").lower()

    if auth_method == "none":
        return NoAuth()

    elif auth_method == "basic":
        username = auth_config.get("username")
        password = auth_config.get("password")
        if not username or not password:
            raise ValueError("Basic auth requires 'username' and 'password'")
        return BasicAuth(username, password)

    elif auth_method == "token":
        token = auth_config.get("token")
        if not token:
            raise ValueError("Token auth requires 'token'")
        return TokenAuth(token)

    elif auth_method == "keycloak":
        required_fields = [
            "server_url",
            "realm",
            "client_id",
            "client_secret",
            "username",
            "password",
        ]
        missing_fields = [field for field in required_fields if not auth_config.get(field)]

        if missing_fields:
            raise ValueError(f"Keycloak auth requires: {', '.join(missing_fields)}")

        return KeycloakAuth(
            server_url=auth_config["server_url"],
            realm=auth_config["realm"],
            client_id=auth_config["client_id"],
            client_secret=auth_config["client_secret"],
            username=auth_config["username"],
            password=auth_config["password"],
        )

    else:
        raise ValueError(f"Unknown authentication method: {auth_method}")
