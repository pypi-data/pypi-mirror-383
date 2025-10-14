"""External API client for notifying about discovered APIs."""

import requests
from typing import Dict, Any, Optional


class APIClient:
    """Client for interacting with external API endpoints."""

    def __init__(
        self,
        endpoint: str,
        auth_token: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize API client.

        Args:
            endpoint: External API endpoint URL.
            auth_token: Authentication token (optional).
            timeout: Request timeout in seconds.
        """
        self.endpoint = endpoint
        self.auth_token = auth_token
        self.timeout = timeout

    def send_openapi_spec(
        self,
        openapi_spec: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send OpenAPI specification to external API.

        Args:
            openapi_spec: OpenAPI specification as dictionary.
            metadata: Additional metadata to send (optional).

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.endpoint:
            print("Warning: No external API endpoint configured. Skipping upload.")
            return False

        try:
            # Prepare payload
            payload = {
                "openapi_spec": openapi_spec,
            }

            if metadata:
                payload["metadata"] = metadata

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
            }

            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"

            # Send request
            print(f"Sending OpenAPI specification to {self.endpoint}...")
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            # Check response
            response.raise_for_status()

            print(f"✓ Successfully sent OpenAPI specification to external API")
            print(f"  Response: {response.status_code}")

            # Log response data if available
            if response.text:
                print(f"  Response data: {response.text[:200]}")

            return True

        except requests.exceptions.Timeout:
            print(f"✗ Error: Request to {self.endpoint} timed out after {self.timeout}s")
            return False

        except requests.exceptions.ConnectionError:
            print(f"✗ Error: Could not connect to {self.endpoint}")
            return False

        except requests.exceptions.HTTPError as e:
            print(f"✗ HTTP Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text[:200]}")
            return False

        except Exception as e:
            print(f"✗ Unexpected error sending to external API: {e}")
            return False

    def send_discovery_event(
        self,
        event_type: str,
        data: Dict[str, Any],
    ) -> bool:
        """
        Send a discovery event to external API.

        Args:
            event_type: Type of event (e.g., "api_discovered", "api_updated").
            data: Event data.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.endpoint:
            print("Warning: No external API endpoint configured. Skipping event.")
            return False

        try:
            payload = {
                "event_type": event_type,
                "data": data,
            }

            headers = {
                "Content-Type": "application/json",
            }

            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"

            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            response.raise_for_status()
            print(f"✓ Successfully sent {event_type} event to external API")
            return True

        except Exception as e:
            print(f"✗ Error sending event to external API: {e}")
            return False

    def health_check(self) -> bool:
        """
        Check if the external API is reachable.

        Returns:
            bool: True if API is healthy, False otherwise.
        """
        if not self.endpoint:
            return False

        try:
            # Try to send a HEAD or GET request to the endpoint
            response = requests.head(self.endpoint, timeout=5)
            return response.status_code < 500
        except:
            return False

