"""Public package interface for the PyFskElec client library."""

from __future__ import annotations

from .client import ArmMEClient, new_session_id
from .exceptions import ArmMEAuthError, ArmMEError, ArmMERequestError
from .models import (
    AccountProfile,
    AccountSubscriptions,
    ApiFailure,
    AppVersionInfo,
    CompanyInfo,
    ComSettingStatus,
    ComStatus,
    DeviceCapability,
    DeviceConfigNames,
    DeviceNotificationSubscriptions,
    DeviceOpenInfo,
    DeviceProperties,
    DeviceSummary,
    OperationResult,
    PartitionAccess,
    PartitionStatus,
    PingResult,
    TokenBundle,
    ZoneStatus,
)

__all__ = [
    "AccountProfile",
    "AccountSubscriptions",
    "ApiFailure",
    "AppVersionInfo",
    "ArmMEAuthError",
    "ArmMEClient",
    "ArmMEError",
    "ArmMERequestError",
    "ComSettingStatus",
    "ComStatus",
    "CompanyInfo",
    "DeviceCapability",
    "DeviceConfigNames",
    "DeviceNotificationSubscriptions",
    "DeviceOpenInfo",
    "DeviceProperties",
    "DeviceSummary",
    "OperationResult",
    "PartitionAccess",
    "PartitionStatus",
    "PingResult",
    "TokenBundle",
    "ZoneStatus",
    "new_session_id",
]
