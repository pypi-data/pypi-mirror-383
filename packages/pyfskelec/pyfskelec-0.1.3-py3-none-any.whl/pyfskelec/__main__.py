"""Command-line entry point for the PyFskElec client."""

from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
from getpass import getpass
import json
import logging
import sys
from typing import Any

from .client import ArmMEClient
from .const import (
    DEFAULT_BASE_URL,
    DEFAULT_CLIENT_ID,
    DEFAULT_CLIENT_SECRET,
    DEFAULT_USER_AGENT,
)
from .exceptions import ArmMEAuthError, ArmMERequestError

LOGGER = logging.getLogger("pyfskelec.cli")


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def _normalise(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, dict):
        return {k: _normalise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalise(v) for v in value]
    return value



def _print_json(payload: Any) -> None:
    normalised = _normalise(payload)
    if isinstance(normalised, (dict, list, tuple)):
        json.dump(normalised, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        LOGGER.info("%s", normalised)


def build_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser."""
    parser = argparse.ArgumentParser(description="PyFskElec API helper")
    parser.add_argument("email", help="Account email / username")
    parser.add_argument("serial", nargs="?", help="Panel serial number to target")
    parser.add_argument("panel_code", help="Panel code for secure actions")
    parser.add_argument(
        "-p",
        "--password",
        help="Account password (omit to be prompted)",
    )
    parser.add_argument(
        "--client-id",
        default=DEFAULT_CLIENT_ID,
        help="OAuth client_id (default: %(default)s)",
    )
    parser.add_argument(
        "--client-secret",
        default=DEFAULT_CLIENT_SECRET,
        help="OAuth client secret (default: hidden)",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override base URL (default: library default)",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="HTTP User-Agent header (default: %(default)s)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Execute the CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    base_url = args.base_url or DEFAULT_BASE_URL
    client_secret = args.client_secret or DEFAULT_CLIENT_SECRET
    client_id = args.client_id or DEFAULT_CLIENT_ID
    user_agent = args.user_agent or DEFAULT_USER_AGENT
    client = ArmMEClient(
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )

    try:
        password = args.password or getpass("Password: ")
        client.login_password(args.email, password)
        profile = client.get_account_profile()
        LOGGER.info("Authenticated as %s %s", profile.first_name, profile.last_name)
        devices = client.list_devices()
        LOGGER.info("Found %s devices", len(devices))

        if not devices:
            return 0

        target = None
        if args.serial:
            target = next((d for d in devices if d.serial_no == args.serial), None)
            if not target:
                LOGGER.error("No device with serial %s", args.serial)
                return 1
        else:
            target = devices[0]

        _print_json(target.__dict__)

        LOGGER.info("Polling panel %s", target.serial_no)
        client.poll_loop(
            target,
            args.panel_code,
        )

    except ArmMEAuthError as exc:
        LOGGER.error("Authentication failed: %s", exc)
        return 2
    except ArmMERequestError as exc:
        LOGGER.error("API error: %s", exc)
        return 3

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
