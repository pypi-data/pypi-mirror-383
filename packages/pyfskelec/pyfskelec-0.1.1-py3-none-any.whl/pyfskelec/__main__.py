"""Command-line entry point for the PyFskElec client."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any

from .client import ArmMEClient
from .const import DEFAULT_BASE_URL, DEFAULT_CLIENT_ID, DEFAULT_USER_AGENT
from .exceptions import ArmMEAuthError, ArmMERequestError

LOGGER = logging.getLogger("pyfskelec.cli")


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def _print_json(payload: Any) -> None:
    if isinstance(payload, (dict, list, tuple)):
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        LOGGER.info("%s", payload)


def build_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser."""
    parser = argparse.ArgumentParser(description="PyFskElec API helper")
    parser.add_argument("email", help="Account email / username")
    parser.add_argument("password", help="Account password")
    parser.add_argument("serial", nargs="?", help="Panel serial number to target")
    parser.add_argument("panel_code", nargs="?", help="Panel code for secure actions")
    parser.add_argument(
        "--client-id",
        default=DEFAULT_CLIENT_ID,
        help="OAuth client_id (default: %(default)s)",
    )
    parser.add_argument(
        "--client-secret",
        default=None,
        help="OAuth client secret (default: library default)",
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

    client = ArmMEClient(
        base_url=args.base_url or DEFAULT_BASE_URL,
        client_id=args.client_id,
        client_secret=args.client_secret,
        user_agent=args.user_agent,
    )

    try:
        client.login_password(args.email, args.password)
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

        if args.panel_code:
            open_info = client.open_connection(
                target.device_id,
                target.device_type_id,
                args.panel_code,
            )
            LOGGER.info(
                "Opened connection: version=%s serial_state=%s",
                open_info.version_number,
                open_info.serial_state,
            )
            client.close_connection(target.device_id)

    except ArmMEAuthError as exc:
        LOGGER.error("Authentication failed: %s", exc)
        return 2
    except ArmMERequestError as exc:
        LOGGER.error("API error: %s", exc)
        return 3

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
