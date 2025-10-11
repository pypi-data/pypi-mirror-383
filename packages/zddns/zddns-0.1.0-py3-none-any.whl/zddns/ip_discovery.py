"""External IP address discovery functionality."""

import logging
import random
from typing import List

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class IPDiscoveryError(Exception):
    """Exception raised when IP discovery fails."""


def get_external_ip(providers: List[str]) -> str:
    """
    Discover the external IP address using one of the provided services.

    Args:
        providers: List of URLs that return the external IP address.

    Returns:
        The external IP address as a string.

    Raises:
        IPDiscoveryError: If the IP address could not be discovered.
    """
    if not providers:
        raise IPDiscoveryError("No IP providers specified")

    # Shuffle the providers to distribute load
    random_providers = providers.copy()
    random.shuffle(random_providers)

    errors = []

    for provider in random_providers:
        try:
            logger.debug("Attempting to get IP from %s", provider)
            response = requests.get(provider, timeout=10)
            response.raise_for_status()

            ip = response.text.strip()
            logger.debug("Got IP: %s", ip)

            # Basic validation of IP format
            if is_valid_ip(ip):
                return ip
            logger.warning("Invalid IP format received from %s: %s", provider, ip)
            errors.append(f"Invalid IP format from {provider}: {ip}")
        except RequestException as e:
            logger.warning("Failed to get IP from %s: %s", provider, e)
            errors.append(f"Error from {provider}: {e}")
        except (ValueError, TypeError) as e:
            logger.warning("Data error from %s: %s", provider, e)
            errors.append(f"Data error from {provider}: {e}")
        except (IOError, ConnectionError) as e:
            logger.warning("Connection error from %s: %s", provider, e)
            errors.append(f"Connection error from {provider}: {e}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            # We need to catch all exceptions to ensure the function doesn't crash
            # This is acceptable here as we're handling external API calls
            logger.warning("Unexpected error from %s: %s", provider, e)
            errors.append(f"Unexpected error from {provider}: {e}")

    # If we get here, all providers failed
    error_msg = "Failed to discover external IP address. Errors:\n" + "\n".join(errors)
    logger.error(error_msg)
    raise IPDiscoveryError(error_msg)


def is_valid_ip(ip: str) -> bool:
    """
    Perform basic validation of an IPv4 or IPv6 address.

    Args:
        ip: The IP address to validate.

    Returns:
        True if the IP appears to be valid, False otherwise.
    """
    # Very basic validation - just check if it looks like an IP address
    # For a production app, consider using the ipaddress module for proper validation

    # Refactored to reduce the number of return statements
    is_valid = False
    # Check for IPv4
    if "." in ip:
        parts = ip.split(".")
        if len(parts) == 4:
            try:
                is_valid = all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
            except (ValueError, TypeError):
                is_valid = False
    # Check for IPv6 (basic check)
    elif ":" in ip:
        is_valid = _validate_ipv6(ip)

    return is_valid


def _validate_ipv6(ip: str) -> bool:
    """
    Helper function to validate IPv6 addresses.
    
    Args:
        ip: The IP address to validate.
        
    Returns:
        True if the IP appears to be a valid IPv6 address, False otherwise.
    """
    # pylint: disable=too-many-nested-blocks
    # Basic IPv6 validation - check for valid format
    parts = ip.split(":")
    # IPv6 can have at most 8 parts, or 9 if there's a double colon
    if len(parts) > 9:
        return False
    # Check if there's a valid number of empty parts (for ::)
    empty_parts = parts.count("")
    if empty_parts > 3:  # At most one :: and possibly empty at start/end
        return False
    # Check each part is a valid hex value
    try:
        for part in parts:
            if part != "":
                # Each part should be a valid hex value of at most 4 digits
                if (len(part) > 4 or
                    not all(c in "0123456789abcdefABCDEF" for c in part)):
                    return False
        return True
    except (ValueError, TypeError):
        return False
