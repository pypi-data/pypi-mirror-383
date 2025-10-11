"""Cloudflare DNS update functionality."""

import logging
from typing import Any, Dict

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class CloudflareError(Exception):
    """Exception raised for Cloudflare API errors."""


class CloudflareDNS:
    """Class for interacting with Cloudflare DNS API."""

    def __init__(self, api_token: str, zone_id: str):
        """
        Initialize the Cloudflare DNS client.

        Args:
            api_token: Cloudflare API token.
            zone_id: Cloudflare Zone ID.
        """
        self.api_token = api_token
        self.zone_id = zone_id
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def get_record_details(self, record_name: str) -> Dict[str, Any]:
        """
        Get details of a DNS record.

        Args:
            record_name: The name of the DNS record.

        Returns:
            Dict containing the record details.

        Raises:
            CloudflareError: If the record could not be found or the API request failed.
        """
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records"
        params = {"name": record_name}

        try:
            response = requests.get(
                url, headers=self.headers, params=params, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if not data["success"]:
                error_msg = ", ".join([err["message"] for err in data["errors"]])
                raise CloudflareError(f"Cloudflare API error: {error_msg}")

            records = data["result"]
            if not records:
                raise CloudflareError(f"DNS record not found: {record_name}")

            return records[0]  # type: ignore[no-any-return]
        except RequestException as e:
            raise CloudflareError(f"Failed to get DNS record: {e}") from e

    def update_record(
        self, record_id: str, record_name: str, ip_address: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Update a DNS record with a new IP address.

        Args:
            record_id: The ID of the DNS record.
            record_name: The name of the DNS record.
            ip_address: The new IP address.
            **kwargs: Additional parameters:
                record_type: The type of DNS record (default: "A").
                ttl: Time to live in seconds (default: 1 for automatic).
                proxied: Whether the record is proxied through Cloudflare (default: False).

        Returns:
            Dict containing the updated record details.

        Raises:
            CloudflareError: If the record could not be updated or the API request failed.
        """
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}"
        # Set default values
        record_type = kwargs.get("record_type", "A")
        ttl = kwargs.get("ttl", 1)
        proxied = kwargs.get("proxied", False)
        data = {
            "type": record_type,
            "name": record_name,
            "content": ip_address,
            "ttl": ttl,
            "proxied": proxied,
        }

        try:
            response = requests.put(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            if not result["success"]:
                error_msg = ", ".join([err["message"] for err in result["errors"]])
                raise CloudflareError(f"Cloudflare API error: {error_msg}")

            logger.info("Updated DNS record %s to %s", record_name, ip_address)
            return result["result"]  # type: ignore[no-any-return]
        except RequestException as e:
            raise CloudflareError(f"Failed to update DNS record: {e}") from e

    def update_record_by_name(
        self, record_name: str, ip_address: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Update a DNS record by name with a new IP address.

        Args:
            record_name: The name of the DNS record.
            ip_address: The new IP address.
            **kwargs: Additional parameters:
                record_type: The type of DNS record (default: "A").
                ttl: Time to live in seconds (default: 1 for automatic).
                proxied: Whether the record is proxied through Cloudflare (default: False).

        Returns:
            Dict containing the updated record details.

        Raises:
            CloudflareError: If the record could not be updated or the API request failed.
        """
        record = self.get_record_details(record_name)

        # Check if the IP is already set correctly
        if record["content"] == ip_address:
            logger.info(
                "DNS record %s already set to %s, no update needed",
                record_name,
                ip_address,
            )
            return record

        return self.update_record(record["id"], record_name, ip_address, **kwargs)
