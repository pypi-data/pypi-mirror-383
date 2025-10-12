"""Exception hierarchy for the PyFskElec client."""

from __future__ import annotations


class ArmMEError(Exception):
    """Base exception for PyFskElec client failures."""


class ArmMEAuthError(ArmMEError):
    """Raised when authentication, login, or token refresh fails."""


class ArmMERequestError(ArmMEError):
    """Raised for non-auth related HTTP errors reported by the API."""

