"""
SensorThings API client for fetching entities from FROST-Server.
Handles pagination, filtering, and authentication.
"""

import logging
from collections.abc import Iterator
from typing import Any, Optional
from urllib.parse import parse_qs, urljoin, urlparse

import requests

from .auth import BasicAuth, FrostAuth, NoAuth

logger = logging.getLogger(__name__)


class SensorThingsAPIClient:
    """Client for interacting with SensorThings API endpoints."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        auth_strategy: Optional[FrostAuth] = None,
    ):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the SensorThings API (e.g., "http://localhost:8080/FROST-Server/v1.1")
            timeout: Request timeout in seconds
            auth_strategy: Authentication strategy instance
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        if auth_strategy:
            self.auth_strategy = auth_strategy
        else:
            self.auth_strategy = NoAuth()

        # Set up session for BasicAuth if needed
        if isinstance(self.auth_strategy, BasicAuth):
            self.session.auth = self.auth_strategy.get_auth_tuple()

        # Set default headers
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": "SensorThings-Validator/1.0"}
        )

    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> dict[str, Any]:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint (e.g., "Things")
            params: Optional query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.RequestException: If request fails
        """
        url = urljoin(self.base_url + "/", endpoint)

        auth_headers = self.auth_strategy.get_headers()

        try:
            logger.debug(f"Making request to: {url} with params: {params}")

            headers = {**self.session.headers, **auth_headers}

            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)

            logger.debug(
                f"Response status: {response.status_code}, Content-Type: {response.headers.get('Content-Type', 'unknown')}"
            )

            response.raise_for_status()

            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as json_err:
                logger.error(f"Failed to parse JSON response from {url}")
                logger.error(f"Response status: {response.status_code}")
                logger.error(f"Response headers: {dict(response.headers)}")
                logger.error(f"Response body (first 500 chars): {response.text[:500]}")
                raise ValueError(
                    f"Server returned non-JSON response (status {response.status_code}). This may indicate an authentication or configuration issue."
                ) from json_err

        except requests.HTTPError as e:
            if e.response.status_code in (401, 403):
                logger.warning(f"Authentication failed for {url}: {e}")
                self.auth_strategy.handle_auth_error(e.response)

                try:
                    logger.debug(f"Retrying request to: {url}")
                    auth_headers = self.auth_strategy.get_headers()
                    headers = {**self.session.headers, **auth_headers}
                    response = self.session.get(
                        url, params=params, headers=headers, timeout=self.timeout
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.RequestException as retry_error:
                    logger.error(f"Retry failed for {url}: {retry_error}")
                    raise

            logger.error(f"API request failed: {url}, Error: {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"API request failed: {url}, Error: {e}")
            raise

    def get_entities(
        self,
        entity_type: str,
        limit: Optional[int] = None,
        select: Optional[list[str]] = None,
        filter_expr: Optional[str] = None,
    ) -> Iterator[dict[str, Any]]:
        """
        Get all entities of a specific type with pagination support.

        Args:
            entity_type: Type of entity (Things, Sensors, Observations, etc.)
            limit: Maximum number of entities to retrieve (None for all)
            select: List of properties to select
            filter_expr: OData filter expression

        Yields:
            Individual entity dictionaries
        """
        params = {}

        if select:
            params["$select"] = ",".join(select)

        if filter_expr:
            params["$filter"] = filter_expr

        # Set initial page size (SensorThings API default is usually 100)
        params["$top"] = min(1000, limit) if limit else 1000

        total_retrieved = 0
        next_url = entity_type

        while next_url and (limit is None or total_retrieved < limit):
            if next_url.startswith("http"):
                # Handle full URL from @iot.nextLink
                parsed_url = urlparse(next_url)
                endpoint = parsed_url.path.replace(urlparse(self.base_url).path, "").lstrip("/")
                query_params = parse_qs(parsed_url.query)
                for key, value_list in query_params.items():
                    params[key] = value_list[0] if len(value_list) == 1 else value_list
            else:
                endpoint = next_url

            try:
                response = self._make_request(endpoint, params)

                entities = response.get("value", [])

                for entity in entities:
                    if limit and total_retrieved >= limit:
                        return

                    yield entity
                    total_retrieved += 1

                next_url = response.get("@iot.nextLink")
                if next_url:
                    params = {}

                logger.debug(f"Retrieved {len(entities)} entities, total: {total_retrieved}")

            except requests.RequestException as e:
                logger.error(f"Failed to fetch entities: {e}")
                break

    def get_entity_by_id(
        self, entity_type: str, entity_id: str, select: Optional[list[str]] = None
    ) -> Optional[dict[str, Any]]:
        """
        Get a specific entity by its ID.

        Args:
            entity_type: Type of entity (Things, Sensors, etc.)
            entity_id: Entity ID
            select: List of properties to select

        Returns:
            Entity dictionary or None if not found
        """
        params = {}
        if select:
            params["$select"] = ",".join(select)

        endpoint = f"{entity_type}({entity_id})"

        try:
            return self._make_request(endpoint, params)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Entity not found: {entity_type}({entity_id})")
                return None
            raise

    def get_entity_count(self, entity_type: str, filter_expr: Optional[str] = None) -> int:
        """
        Get the total count of entities.

        Args:
            entity_type: Type of entity
            filter_expr: Optional filter expression

        Returns:
            Total count of entities
        """
        params = {"$count": "true", "$top": "0"}

        if filter_expr:
            params["$filter"] = filter_expr

        try:
            response = self._make_request(entity_type, params)
            return response.get("@iot.count", 0)
        except requests.RequestException:
            logger.warning(f"Could not get count for {entity_type}, falling back to enumeration")

            return sum(1 for _ in self.get_entities(entity_type, filter_expr=filter_expr))

    def test_connection(self) -> bool:
        """
        Test the connection to the SensorThings API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._make_request("")
            logger.info("Successfully connected to SensorThings API")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_service_root(self) -> dict[str, Any]:
        """
        Get the service root document.

        Returns:
            Service root document
        """
        return self._make_request("")

    def get_available_entity_types(self) -> list[str]:
        """
        Get list of available entity types from the service root.

        Returns:
            List of entity type names
        """
        try:
            service_root = self.get_service_root()
            entity_types = []

            logger.debug(f"Service root keys: {list(service_root.keys())}")

            for key, value in service_root.items():
                logger.debug(f"Checking key: {key}, value type: {type(value)}, value: {value}")
                if isinstance(value, dict) and "url" in value:
                    url = value["url"]
                    if url.startswith(self.base_url):
                        entity_type = url.replace(self.base_url + "/", "")
                        if entity_type and not entity_type.startswith("$"):
                            entity_types.append(entity_type)
                            logger.debug(f"Added entity type from dict: {entity_type}")
                elif isinstance(value, str) and value.startswith(self.base_url):
                    entity_type = value.replace(self.base_url + "/", "")
                    if entity_type and not entity_type.startswith("$"):
                        entity_types.append(entity_type)
                        logger.debug(f"Added entity type from string: {entity_type}")
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and "url" in item:
                            url = item["url"]
                            if url.startswith(self.base_url):
                                entity_type = url.replace(self.base_url + "/", "")
                                if entity_type and not entity_type.startswith("$"):
                                    entity_types.append(entity_type)
                                    logger.debug(f"Added entity type from list: {entity_type}")

            logger.info(f"Discovered entity types: {entity_types}")

            if not entity_types:
                logger.warning("No entity types discovered from service root, using fallback list")
                return [
                    "Things",
                    "Sensors",
                    "ObservedProperties",
                    "Observations",
                    "Datastreams",
                    "Locations",
                    "HistoricalLocations",
                    "FeaturesOfInterest",
                ]

            return entity_types
        except Exception as e:
            logger.warning(f"Could not determine entity types: {e}")
            return [
                "Things",
                "Sensors",
                "ObservedProperties",
                "Observations",
                "Datastreams",
                "Locations",
                "HistoricalLocations",
                "FeaturesOfInterest",
            ]
