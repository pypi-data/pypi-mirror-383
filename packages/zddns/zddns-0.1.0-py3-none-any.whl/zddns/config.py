"""Configuration management for ZDDNS."""

import os
import pathlib
from typing import Any, Dict, Optional, Union

import yaml


class ConfigError(Exception):
    """Exception raised for configuration errors."""


def get_default_config_path() -> pathlib.Path:
    """Get the default configuration file path."""
    if os.name == "nt":  # Windows
        config_dir = pathlib.Path(os.environ.get("APPDATA", "")) / "zddns"
    else:  # Unix-like
        config_dir = pathlib.Path.home() / ".config" / "zddns"
    return config_dir / "config.yaml"


def load_config(
    config_path: Optional[Union[str, pathlib.Path]] = None,
) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file. If None, uses the default path.

    Returns:
        Dict containing the configuration.

    Raises:
        ConfigError: If the configuration file is invalid or missing required fields.
    """
    if config_path is None:
        config_path = get_default_config_path()
    else:
        config_path = pathlib.Path(config_path)

    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise ConfigError(f"Failed to load configuration: {e}") from e

    # Validate configuration
    validate_config(config)

    # Set defaults
    set_config_defaults(config)

    return config  # type: ignore[no-any-return]


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration.

    Args:
        config: Configuration dictionary.

    Raises:
        ConfigError: If the configuration is invalid.
    """
    # Check for required sections
    if not isinstance(config, dict):
        raise ConfigError("Configuration must be a dictionary")

    if "cloudflare" not in config:
        raise ConfigError("Missing 'cloudflare' section in configuration")

    # Check Cloudflare configuration
    cf = config["cloudflare"]
    if not isinstance(cf, dict):
        raise ConfigError("'cloudflare' section must be a dictionary")

    for field in ["api_token", "zone_id", "record_name"]:
        if field not in cf:
            raise ConfigError(
                f"Missing required field '{field}' in 'cloudflare' section"
            )

    # Check IP providers
    if "ip_providers" in config:
        if not isinstance(config["ip_providers"], list) or not config["ip_providers"]:
            raise ConfigError("'ip_providers' must be a non-empty list")

    # Check check_interval
    if "check_interval" in config:
        if (
            not isinstance(config["check_interval"], (int, float))
            or config["check_interval"] <= 0
        ):
            raise ConfigError("'check_interval' must be a positive number")


def set_config_defaults(config: Dict[str, Any]) -> None:
    """
    Set default values for optional configuration fields.

    Args:
        config: Configuration dictionary.
    """
    # Default IP providers
    if "ip_providers" not in config:
        config["ip_providers"] = [
            "https://api.ipify.org",
            "https://ifconfig.me/ip",
            "https://icanhazip.com",
        ]

    # Default check interval (5 minutes)
    if "check_interval" not in config:
        config["check_interval"] = 300

    # Cloudflare defaults
    cf = config["cloudflare"]
    if "ttl" not in cf:
        cf["ttl"] = 1  # Auto

    if "proxied" not in cf:
        cf["proxied"] = False
