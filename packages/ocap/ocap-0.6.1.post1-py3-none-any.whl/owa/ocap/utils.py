import os
import sys
import time
from typing import Optional

import requests
from loguru import logger
from packaging.version import parse as parse_version
from rich import print


def get_local_version(package_name: str = "ocap") -> str:
    """Get the version of the locally installed package."""
    if sys.version_info >= (3, 8):
        from importlib.metadata import version
    else:
        from importlib_metadata import version

    try:
        __version__ = version(package_name)
    except Exception:
        __version__ = "unknown"

    return __version__


def get_latest_release(
    url: str = "https://api.github.com/repos/open-world-agents/open-world-agents/releases/latest",
) -> str:
    """Get the latest release version from GitHub."""
    # Skip GitHub API call if disabled via environment variable (e.g., during testing)
    if os.environ.get("OWA_DISABLE_VERSION_CHECK"):
        return get_local_version()  # Return the locally installed version as the default

    response = requests.get(url, timeout=5)
    response.raise_for_status()
    tag = response.json()["tag_name"]
    return tag.lstrip("v")  # Remove leading "v" if present


def check_for_update(
    package_name: str = "ocap",
    *,
    silent: bool = False,
    url: str = "https://api.github.com/repos/open-world-agents/ocap/releases/latest",
) -> bool:
    """
    Check for updates and print a message if a new version is available.

    Args:
        package_name: Name of the package to check
        silent: If True, suppress all output
        url: URL to check for the latest release

    Returns:
        bool: True if the local version is up to date, False otherwise.
    """
    # Skip version check if disabled via environment variable (e.g., during testing)
    if os.environ.get("OWA_DISABLE_VERSION_CHECK"):
        return True

    try:
        local_version = get_local_version(package_name)
        latest_version = get_latest_release(url)
        if parse_version(latest_version) > parse_version(local_version):
            if not silent:
                print(f"""
[bold red]******************************************************[/bold red]
[bold yellow]   An update is available for Open World Agents![/bold yellow]
[bold red]******************************************************[/bold red]
[bold]  Your version:[/bold] [red]{local_version}[/red]    [bold]Latest:[/bold] [green]{latest_version}[/green]
  Get it here: [bold cyan]https://github.com/open-world-agents/ocap/releases[/bold cyan]
""")
            return False
        else:
            return True
    except requests.Timeout as e:
        if not silent:
            print(f"[bold red]⚠ Error:[/bold red] Unable to check for updates. Timeout occurred: {e}")
    except requests.RequestException as e:
        if not silent:
            print(f"[bold red]⚠ Error:[/bold red] Unable to check for updates. Request failed: {e}")
    except Exception as e:
        if not silent:
            print(f"[bold red]⚠ Error:[/bold red] Unable to check for updates. An unexpected error occurred: {e}")
    return False


def countdown_delay(seconds: float):
    """Display a countdown before starting recording."""
    if seconds <= 0:
        return

    logger.info(f"⏱️ Recording will start in {seconds} seconds...")

    # Show countdown for delays >= 3 seconds
    if seconds >= 3:
        for i in range(int(seconds), 0, -1):
            logger.info(f"Starting in {i}...")
            time.sleep(1)
        # Handle fractional part
        remaining = seconds - int(seconds)
        if remaining > 0:
            time.sleep(remaining)
    else:
        time.sleep(seconds)

    logger.info("🎬 Recording started!")


def parse_additional_properties(additional_args: Optional[str]) -> dict:
    """Parse additional arguments string into a dictionary of properties."""
    additional_properties = {}
    if additional_args is not None:
        for arg in additional_args.split(","):
            key, value = arg.split("=")
            additional_properties[key] = value
    return additional_properties
