"""Main application logic for ZDDNS."""

import logging
import time
from typing import Optional

from zddns.cloudflare import CloudflareDNS, CloudflareError
from zddns.config import load_config
from zddns.ip_discovery import IPDiscoveryError, get_external_ip

logger = logging.getLogger(__name__)


class ZDDNSApp:
    """Main application class for ZDDNS."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the ZDDNS application.

        Args:
            config_path: Path to the configuration file. If None, uses the default path.

        Raises:
            ConfigError: If the configuration file is invalid or missing.
        """
        self.config = load_config(config_path)
        self.cf_config = self.config["cloudflare"]
        self.ip_providers = self.config["ip_providers"]
        self.check_interval = self.config["check_interval"]

        self.cf_client = CloudflareDNS(
            api_token=self.cf_config["api_token"],
            zone_id=self.cf_config["zone_id"],
        )

        self.current_ip: Optional[str] = None

    def update_dns_once(self, dry_run: bool = False) -> bool:
        """
        Perform a single DNS update.

        Args:
            dry_run: If True, only simulate the update without making actual changes.

        Returns:
            True if the update was successful or not needed, False otherwise.
        """
        try:
            # Get the external IP
            ip_address = get_external_ip(self.ip_providers)

            # If the IP hasn't changed, no need to update
            if self.current_ip == ip_address:
                logger.info("IP address unchanged: %s", ip_address)
                return True

            if dry_run:
                logger.info(
                    "[DRY RUN] Would update DNS record %s to %s",
                    self.cf_config["record_name"],
                    ip_address,
                )
                return True

            # Update the DNS record
            self.cf_client.update_record_by_name(
                record_name=self.cf_config["record_name"],
                ip_address=ip_address,
                ttl=self.cf_config.get("ttl", 1),
                proxied=self.cf_config.get("proxied", False),
            )

            # Update the current IP
            self.current_ip = ip_address
            return True

        except (IPDiscoveryError, CloudflareError) as e:
            logger.error("Failed to update DNS: %s", e)
            return False

    def run(self, once: bool = False, dry_run: bool = False) -> None:
        """
        Run the ZDDNS application.

        Args:
            once: If True, run once and exit. If False, run continuously.
            dry_run: If True, only simulate the update without making actual changes.
        """
        if dry_run:
            logger.info("Running in DRY RUN mode - no actual changes will be made")

        if once:
            logger.info("Running ZDDNS once")
            self.update_dns_once(dry_run=dry_run)
            return

        logger.info(
            "Starting ZDDNS with check interval of %s seconds", self.check_interval
        )

        while True:
            try:
                self.update_dns_once(dry_run=dry_run)
            except (IPDiscoveryError, CloudflareError) as e:
                logger.error("Error during DNS update: %s", e)
            except (IOError, OSError) as e:
                logger.error("System error: %s", e)
            except (ValueError, TypeError) as e:
                logger.error("Data error: %s", e)

            logger.debug("Sleeping for %s seconds", self.check_interval)
            time.sleep(self.check_interval)

    def get_current_ip(self) -> str:
        """
        Get the current external IP address.

        Returns:
            The current external IP address.

        Raises:
            IPDiscoveryError: If the IP address could not be discovered.
        """
        return get_external_ip(self.ip_providers)
