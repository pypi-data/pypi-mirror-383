"""Command-line interface for ZDDNS."""

import logging
import sys
from typing import Optional

import click

from zddns.app import ZDDNSApp
from zddns.config import ConfigError
from zddns.ip_discovery import IPDiscoveryError


def setup_logging(verbose: bool) -> None:
    """
    Set up logging configuration.

    Args:
        verbose: If True, set log level to DEBUG. Otherwise, set to INFO.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler()],
    )


@click.command()
@click.option(
    "--config",
    "-c",
    help="Path to the configuration file.",
    type=click.Path(exists=True, dir_okay=False, readable=True),
)
@click.option(
    "--once",
    "-o",
    is_flag=True,
    help="Run once and exit.",
)
@click.option(
    "--show-ip",
    "-i",
    is_flag=True,
    help="Show the current external IP address and exit.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging.",
)
@click.option(
    "--dry-run",
    "-d",
    is_flag=True,
    help="Simulate updates without making actual changes.",
)
def main(
    config: Optional[str], once: bool, show_ip: bool, verbose: bool, dry_run: bool
) -> None:
    """
    Update Cloudflare DNS records with your network's external IP address.

    This tool automatically discovers your external IP address and updates
    the specified Cloudflare DNS records. Use the --dry-run option to simulate
    updates without making actual changes to your DNS records.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        app = ZDDNSApp(config_path=config)

        if show_ip:
            ip = app.get_current_ip()
            click.echo(
                f"Current external IP address: {ip}"
            )  # f-string is fine for click.echo
            return

        app.run(once=once, dry_run=dry_run)
    except ConfigError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)
    except IPDiscoveryError as e:
        logger.error("IP discovery error: %s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except (IOError, OSError) as e:
        logger.error("System error: %s", e)
        sys.exit(1)
    except (ValueError, TypeError) as e:
        logger.error("Data error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
