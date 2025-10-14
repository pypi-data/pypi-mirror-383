"""
Tests for authentication strategies.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.auth import (
    AuthenticationError,
    BasicAuth,
    KeycloakAuth,
    NoAuth,
    TokenAuth,
    create_auth_strategy,
)


class TestNoAuth:
    """Test suite for NoAuth strategy."""

    def test_get_headers(self):
        """Test that NoAuth returns empty headers."""
        auth = NoAuth()
        headers = auth.get_headers()

        assert headers == {}

    def test_handle_auth_error(self):
        """Test that NoAuth doesn't raise on auth error."""
        auth = NoAuth()
        response = MagicMock(spec=requests.Response)
        response.status_code = 401

        # Should not raise
        auth.handle_auth_error(response)


class TestBasicAuth:
    """Test suite for BasicAuth strategy."""

    def test_init(self):
        """Test BasicAuth initialization."""
        auth = BasicAuth("testuser", "testpass")

        assert auth.username == "testuser"
        assert auth.password == "testpass"
        assert auth._auth_tuple == ("testuser", "testpass")

    def test_get_headers(self):
        """Test that BasicAuth returns empty headers (auth is via tuple)."""
        auth = BasicAuth("testuser", "testpass")
        headers = auth.get_headers()

        # Basic auth uses requests.Session.auth, not headers
        assert headers == {}

    def test_get_auth_tuple(self):
        """Test getting auth tuple for requests."""
        auth = BasicAuth("testuser", "testpass")
        auth_tuple = auth.get_auth_tuple()

        assert auth_tuple == ("testuser", "testpass")

    def test_handle_auth_error(self):
        """Test that BasicAuth doesn't raise on auth error."""
        auth = BasicAuth("testuser", "testpass")
        response = MagicMock(spec=requests.Response)
        response.status_code = 401

        # Should not raise
        auth.handle_auth_error(response)


class TestTokenAuth:
    """Test suite for TokenAuth strategy."""

    def test_init(self):
        """Test TokenAuth initialization."""
        auth = TokenAuth("test-token-12345")

        assert auth.token == "test-token-12345"

    def test_get_headers(self):
        """Test that TokenAuth returns Bearer token in headers."""
        auth = TokenAuth("test-token-12345")
        headers = auth.get_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token-12345"

    def test_handle_auth_error(self):
        """Test that TokenAuth doesn't raise on auth error."""
        auth = TokenAuth("test-token-12345")
        response = MagicMock(spec=requests.Response)
        response.status_code = 401

        # Should not raise
        auth.handle_auth_error(response)


class TestKeycloakAuth:
    """Test suite for KeycloakAuth strategy."""

    def test_init(self):
        """Test KeycloakAuth initialization."""
        auth = KeycloakAuth(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            username="testuser",
            password="testpass",
        )

        assert auth.server_url == "https://keycloak.example.com"
        assert auth.realm == "test-realm"
        assert auth.client_id == "test-client"
        assert auth.username == "testuser"
        assert auth.access_token is None

    def test_token_url_construction(self):
        """Test that token URL is constructed correctly."""
        auth = KeycloakAuth(
            server_url="https://keycloak.example.com/",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            username="testuser",
            password="testpass",
        )

        expected_url = (
            "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/token"
        )
        assert auth.token_url == expected_url

    @patch("src.auth.requests.post")
    def test_fetch_token_success(self, mock_post):
        """Test successful token fetch from Keycloak."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        auth = KeycloakAuth(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            username="testuser",
            password="testpass",
        )

        auth._fetch_token()

        assert auth.access_token == "test-access-token"
        assert auth.refresh_token == "test-refresh-token"
        assert auth.token_expires_at > 0

    @patch("src.auth.requests.post")
    def test_fetch_token_failure(self, mock_post):
        """Test failed token fetch from Keycloak."""
        # Mock failed response
        mock_post.side_effect = requests.RequestException("Connection error")

        auth = KeycloakAuth(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            username="testuser",
            password="testpass",
        )

        with pytest.raises(AuthenticationError, match="Keycloak authentication failed"):
            auth._fetch_token()

    @patch("src.auth.requests.post")
    def test_get_headers_fetches_token_if_needed(self, mock_post):
        """Test that get_headers fetches token if not present."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test-access-token",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        auth = KeycloakAuth(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            username="testuser",
            password="testpass",
        )

        headers = auth.get_headers()

        assert headers["Authorization"] == "Bearer test-access-token"
        assert mock_post.called

    @patch("src.auth.time.time")
    def test_token_expired(self, mock_time):
        """Test token expiration check."""
        mock_time.return_value = 1000

        auth = KeycloakAuth(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            username="testuser",
            password="testpass",
        )

        auth.access_token = "test-token"
        auth.token_expires_at = 1100  # Expires in 100 seconds

        # Not expired (with 30 second buffer)
        assert auth._token_expired() is False

        # Expired
        auth.token_expires_at = 1020  # Expires in 20 seconds (within buffer)
        assert auth._token_expired() is True

    def test_handle_auth_error_clears_token(self):
        """Test that auth error clears the token."""
        auth = KeycloakAuth(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            username="testuser",
            password="testpass",
        )

        auth.access_token = "test-token"
        auth.token_expires_at = 9999999999

        response = MagicMock(spec=requests.Response)
        response.status_code = 401

        auth.handle_auth_error(response)

        # Token should be cleared
        assert auth.access_token is None
        assert auth.token_expires_at == 0


class TestAuthFactory:
    """Test suite for authentication factory functions."""

    def test_create_auth_strategy_none(self):
        """Test creating NoAuth strategy."""
        auth = create_auth_strategy(None)
        assert isinstance(auth, NoAuth)

        auth = create_auth_strategy({})
        assert isinstance(auth, NoAuth)

        auth = create_auth_strategy({"method": "none"})
        assert isinstance(auth, NoAuth)

    def test_create_auth_strategy_basic(self):
        """Test creating BasicAuth strategy."""
        auth = create_auth_strategy(
            {"method": "basic", "username": "testuser", "password": "testpass"}
        )

        assert isinstance(auth, BasicAuth)
        assert auth.username == "testuser"
        assert auth.password == "testpass"

    def test_create_auth_strategy_basic_missing_credentials(self):
        """Test that BasicAuth requires username and password."""
        with pytest.raises(ValueError, match="Basic auth requires"):
            create_auth_strategy({"method": "basic", "username": "testuser"})

        with pytest.raises(ValueError, match="Basic auth requires"):
            create_auth_strategy({"method": "basic", "password": "testpass"})

    def test_create_auth_strategy_token(self):
        """Test creating TokenAuth strategy."""
        auth = create_auth_strategy({"method": "token", "token": "test-token-12345"})

        assert isinstance(auth, TokenAuth)
        assert auth.token == "test-token-12345"

    def test_create_auth_strategy_token_missing_token(self):
        """Test that TokenAuth requires token."""
        with pytest.raises(ValueError, match="Token auth requires 'token'"):
            create_auth_strategy({"method": "token"})

    def test_create_auth_strategy_keycloak(self):
        """Test creating KeycloakAuth strategy."""
        auth = create_auth_strategy(
            {
                "method": "keycloak",
                "server_url": "https://keycloak.example.com",
                "realm": "test-realm",
                "client_id": "test-client",
                "client_secret": "test-secret",
                "username": "testuser",
                "password": "testpass",
            }
        )

        assert isinstance(auth, KeycloakAuth)
        assert auth.realm == "test-realm"
        assert auth.client_id == "test-client"

    def test_create_auth_strategy_keycloak_missing_fields(self):
        """Test that KeycloakAuth requires all fields."""
        with pytest.raises(ValueError, match="Keycloak auth requires"):
            create_auth_strategy(
                {
                    "method": "keycloak",
                    "server_url": "https://keycloak.example.com",
                    "realm": "test-realm",
                    # Missing other fields
                }
            )

    def test_create_auth_strategy_unknown_method(self):
        """Test that unknown auth method raises error."""
        with pytest.raises(ValueError, match="Unknown authentication method"):
            create_auth_strategy({"method": "unknown"})
