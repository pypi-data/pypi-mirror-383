"""Data models for the PyFskElec API client."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


@dataclass(frozen=True)
class PartitionAccess:
    """Role mapping for a single alarm partition."""

    partition: int
    role: int

    @staticmethod
    def from_json(data: dict[str, Any]) -> PartitionAccess:
        """Return a PartitionAccess parsed from an API payload."""
        return PartitionAccess(
            partition=int(data.get("Partition", 0)),
            role=int(data.get("Role", 0)),
        )


@dataclass(frozen=True)
class DeviceSummary:
    """Top-level alarm device summary returned by the API."""

    name: str
    device_id: int
    serial_no: str
    device_type_name: str
    device_type_id: int
    com_type_name: str
    com_type_id: int
    enabled: bool
    is_rest: bool
    partition_access: list[PartitionAccess]
    version_com: str | None
    version_panel: str | None
    version_config: str | None
    panel_type_id: int | None
    panel_type_name: str | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> DeviceSummary:
        """Return a DeviceSummary parsed from an API payload."""
        partition_access = [
            PartitionAccess.from_json(item)
            for item in (data.get("PartitionAccess") or [])
        ]
        return DeviceSummary(
            name=str(data.get("Name", "")),
            device_id=int(data.get("DeviceId", 0)),
            serial_no=str(data.get("SerialNo", "")),
            device_type_name=str(data.get("DeviceTypeName", "")),
            device_type_id=int(data.get("DeviceTypeId", 0)),
            com_type_name=str(data.get("ComTypeName", "")),
            com_type_id=int(data.get("ComTypeId", 0)),
            enabled=bool(data.get("Enabled", False)),
            is_rest=bool(data.get("IsRest", False)),
            partition_access=partition_access,
            version_com=data.get("VersionCom"),
            version_panel=data.get("VersionPanel"),
            version_config=data.get("VersionConfig"),
            panel_type_id=(
                int(data["PanelTypeId"]) if data.get("PanelTypeId") is not None else None
            ),
            panel_type_name=data.get("PanelTypeName"),
        )


@dataclass
class TokenBundle:
    """OAuth token bundle returned from the /Token endpoint."""

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None
    client_id: str | None = None
    email: str | None = None
    first_name: str | None = None
    user_role: str | None = None
    raw: dict[str, Any] | None = None

    @staticmethod
    def from_json(data: dict[str, Any]) -> TokenBundle:
        """Return a TokenBundle parsed from an API payload."""
        return TokenBundle(
            access_token=data["access_token"],
            token_type=data.get("token_type", "bearer"),
            expires_in=int(data.get("expires_in", 3600)),
            refresh_token=data.get("refresh_token"),
            client_id=data.get("as:client_id"),
            email=data.get("Email"),
            first_name=data.get("FirstName") or data.get("name"),
            user_role=data.get("user_role"),
            raw=data,
        )


@dataclass(frozen=True)
class OperationResult:
    """Generic success/failure payload returned by many endpoints."""

    succeeded: bool
    message: str
    custom_error_code: int
    model_errors: dict[str, Any] | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> OperationResult:
        """Return an OperationResult parsed from an API payload."""
        return OperationResult(
            succeeded=bool(data.get("Succeeded", False)),
            message=str(data.get("Message", "")),
            custom_error_code=int(data.get("CustomErrorCode", 0)),
            model_errors=data.get("ModelErrors"),
        )


@dataclass(frozen=True)
class DeviceCapability:
    """Describes the supported operations and counts of a device."""

    device_type_id: int
    device_type_name: str
    com_type_id: int
    com_type_name: str
    panel_type_id: int
    panel_type_name: str
    version_com: str | None
    version_panel: str | None
    partitions: int
    zones: int
    users: int
    stay_arms: int
    com_inputs: int
    com_outputs: int
    panel_outputs: int
    pin_required: bool
    status_delay: int
    min_com_version: str | None
    wireless: bool
    always_available_enabled: bool
    wireless_enabled: bool
    sigfox_enabled: bool
    serial_protocol: str | None
    serial_state: int | None
    serial_ready: bool | None
    is_serial: bool | None
    has_panel: bool | None
    rest_api: bool | None
    partition_status: bool
    partition_all_status: bool
    panel_status: bool
    away_arm: bool
    stay_arm: bool
    sleep_arm: bool
    disarm: bool
    reset: bool
    panic: bool
    zone_status: bool
    zone_partition_status: bool
    zone_bypass: bool
    panel_output_status: bool
    panel_output_set: bool
    com_status: bool
    com_output_set: bool
    is_premium: bool

    @staticmethod
    def from_json(data: dict[str, Any]) -> DeviceCapability:
        """Return a DeviceCapability parsed from an API payload."""
        get_value = data.get
        serial_state_raw = get_value("SerialState")
        return DeviceCapability(
            device_type_id=int(get_value("DeviceTypeId", 0)),
            device_type_name=str(get_value("DeviceTypeName", "")),
            com_type_id=int(get_value("ComTypeId", 0)),
            com_type_name=str(get_value("ComTypeName", "")),
            panel_type_id=int(get_value("PanelTypeId", 0)),
            panel_type_name=str(get_value("PanelTypeName", "")),
            version_com=get_value("VersionCom"),
            version_panel=get_value("VersionPanel"),
            partitions=int(get_value("Partitions", 0)),
            zones=int(get_value("Zones", 0)),
            users=int(get_value("Users", 0)),
            stay_arms=int(get_value("StayArms", 0)),
            com_inputs=int(get_value("ComInputs", 0)),
            com_outputs=int(get_value("ComOutputs", 0)),
            panel_outputs=int(get_value("PanelOutputs", 0)),
            pin_required=bool(get_value("PinRequired", False)),
            status_delay=int(get_value("StatusDelay", 0)),
            min_com_version=get_value("MinComVersion"),
            wireless=bool(get_value("Wireless", False)),
            always_available_enabled=bool(get_value("AlwaysAvailableEnabled", False)),
            wireless_enabled=bool(get_value("WirelessEnabled", False)),
            sigfox_enabled=bool(get_value("SigFoxEnabled", False)),
            serial_protocol=get_value("SerialProtocol"),
            serial_state=int(serial_state_raw) if serial_state_raw is not None else None,
            serial_ready=get_value("SerialReady"),
            is_serial=get_value("IsSerial"),
            has_panel=get_value("HasPanel"),
            rest_api=get_value("RestApi"),
            partition_status=bool(get_value("PartitionStatus", False)),
            partition_all_status=bool(get_value("PartitionAllStatus", False)),
            panel_status=bool(get_value("PanelStatus", False)),
            away_arm=bool(get_value("AwayArm", False)),
            stay_arm=bool(get_value("StayArm", False)),
            sleep_arm=bool(get_value("SleepArm", False)),
            disarm=bool(get_value("Disarm", False)),
            reset=bool(get_value("Reset", False)),
            panic=bool(get_value("Panic", False)),
            zone_status=bool(get_value("ZoneStatus", False)),
            zone_partition_status=bool(get_value("ZonePartitionStatus", False)),
            zone_bypass=bool(get_value("ZoneBypass", False)),
            panel_output_status=bool(get_value("PanelOutputStatus", False)),
            panel_output_set=bool(get_value("PanelOutputSet", False)),
            com_status=bool(get_value("ComStatus", False)),
            com_output_set=bool(get_value("ComOutputSet", False)),
            is_premium=bool(get_value("IsPremium", False)),
        )


@dataclass(frozen=True)
class DeviceConfigNames:
    """Human-friendly configuration names tied to a device."""

    device_name: str | None
    zone_names: dict[str, str]
    user_names: dict[str, str]
    input_names: dict[str, str] | None
    output_names: dict[str, str] | None
    button_names: dict[str, str] | None
    partition_names: dict[str, str] | None
    panel_output_names: dict[str, str] | None

    @staticmethod
    def from_json_string(raw: str | None) -> DeviceConfigNames:
        """Return DeviceConfigNames parsed from an embedded JSON string."""
        if not raw:
            return DeviceConfigNames(None, {}, {}, None, None, None, None, None)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return DeviceConfigNames(None, {}, {}, None, None, None, None, None)
        return DeviceConfigNames(
            device_name=payload.get("DeviceName"),
            zone_names=payload.get("ZoneNames", {}) or {},
            user_names=payload.get("UserNames", {}) or {},
            input_names=payload.get("InputNames"),
            output_names=payload.get("OutputNames"),
            button_names=payload.get("ButtonNames"),
            partition_names=payload.get("PartitionNames"),
            panel_output_names=payload.get("PanelOutputNames"),
        )


@dataclass(frozen=True)
class DeviceProperties:
    """Detailed properties for an alarm device."""

    device_id: int
    serial_no: str
    company_id: int
    cl: str | None
    device_type_name: str
    com_type_name: str
    device_type_id: int
    com_type_id: int
    panel_type_id: int
    panel_type_name: str
    enabled: bool
    names: DeviceConfigNames
    partition_access: list[dict[str, int]]
    network: int | None
    ss1: float | None
    ss2: float | None
    serial_protocol: str | None
    serial_state: int | None
    serial_ready: bool | None
    rest_api: bool | None
    always_available_enabled: bool | None
    wireless_enabled: bool | None
    sigfox_enabled: bool | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> DeviceProperties:
        """Return DeviceProperties parsed from an API payload."""
        network_raw = data.get("Network")
        ss1_raw = data.get("SS1")
        ss2_raw = data.get("SS2")
        serial_state_raw = data.get("SerialState")
        return DeviceProperties(
            device_id=int(data.get("DeviceId", 0)),
            serial_no=str(data.get("SerialNo", "")),
            company_id=int(data.get("CompanyId", 0)),
            cl=data.get("CL"),
            device_type_name=str(data.get("DeviceTypeName", "")),
            com_type_name=str(data.get("ComTypeName", "")),
            device_type_id=int(data.get("DeviceTypeId", 0)),
            com_type_id=int(data.get("ComTypeId", 0)),
            panel_type_id=int(data.get("PanelTypeId", 0)),
            panel_type_name=str(data.get("PanelTypeName", "")),
            enabled=bool(data.get("Enabled", False)),
            names=DeviceConfigNames.from_json_string(data.get("DeviceConfig")),
            partition_access=data.get("PartitionAccess") or [],
            network=int(network_raw) if network_raw is not None else None,
            ss1=float(ss1_raw) if ss1_raw is not None else None,
            ss2=float(ss2_raw) if ss2_raw is not None else None,
            serial_protocol=data.get("SerialProtocol"),
            serial_state=int(serial_state_raw)
            if serial_state_raw is not None
            else None,
            serial_ready=data.get("SerialReady"),
            rest_api=data.get("RestApi"),
            always_available_enabled=data.get("AlwaysAvailableEnabled"),
            wireless_enabled=data.get("WirelessEnabled"),
            sigfox_enabled=data.get("SigFoxEnabled"),
        )


@dataclass(frozen=True)
class CompanyInfo:
    """Company metadata associated with a device."""

    company_name: str
    cl: str | None
    company_id: int
    public_logo: str | None
    domain: str | None
    allowed_email_domain: str | None
    portal_subdomain: str | None
    contact_number: str | None
    contact_email: str | None
    emergency_number: str | None
    support_email: str | None
    has_created_theme: bool
    company_theme_id: int | None
    date_last_updated_utc: str | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> CompanyInfo:
        """Return CompanyInfo parsed from an API payload."""
        get_value = data.get
        company_theme_raw = get_value("CompanyThemeId")
        return CompanyInfo(
            company_name=str(get_value("CompanyName", "")),
            cl=get_value("CL"),
            company_id=int(get_value("CompanyId", 0)),
            public_logo=get_value("PublicLogo"),
            domain=get_value("Domain"),
            allowed_email_domain=get_value("AllowedEmailDomain"),
            portal_subdomain=get_value("PortalSubdomain"),
            contact_number=get_value("ContactNumber"),
            contact_email=get_value("ContactEmail"),
            emergency_number=get_value("EmergencyNumber"),
            support_email=get_value("SupportEmail"),
            has_created_theme=bool(get_value("HasCreatedTheme", False)),
            company_theme_id=int(company_theme_raw)
            if company_theme_raw is not None
            else None,
            date_last_updated_utc=get_value("DateLastUpdatedUtc"),
        )


@dataclass(frozen=True)
class PingResult:
    """Result for a device ping request."""

    host: int
    sim: int
    succeeded: bool
    message: str | None
    custom_error_code: int
    model_errors: dict[str, Any] | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> PingResult:
        """Return a PingResult parsed from an API payload."""
        return PingResult(
            host=int(data.get("Host", 0)),
            sim=int(data.get("Sim", 0)),
            succeeded=bool(data.get("Succeeded", False)),
            message=data.get("Message"),
            custom_error_code=int(data.get("CustomErrorCode", 0)),
            model_errors=data.get("ModelErrors"),
        )


@dataclass(frozen=True)
class DeviceOpenInfo:
    """Payload describing connection state after opening a session."""

    ss1: float | None
    ss2: float | None
    always_available_enabled: bool | None
    wireless_enabled: bool | None
    sigfox_enabled: bool | None
    serial_state: int | None
    serial_ready: bool | None
    version_number: str | None
    has_panic: bool | None
    succeeded: bool
    message: str
    custom_error_code: int
    model_errors: dict[str, Any] | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> DeviceOpenInfo:
        """Return DeviceOpenInfo parsed from an API payload."""
        get_value = data.get
        ss1_raw = get_value("SS1")
        ss2_raw = get_value("SS2")
        serial_state_raw = get_value("SerialState")
        return DeviceOpenInfo(
            ss1=float(ss1_raw) if ss1_raw is not None else None,
            ss2=float(ss2_raw) if ss2_raw is not None else None,
            always_available_enabled=get_value("AlwaysAvailableEnabled"),
            wireless_enabled=get_value("WirelessEnabled"),
            sigfox_enabled=get_value("SigFoxEnabled"),
            serial_state=int(serial_state_raw)
            if serial_state_raw is not None
            else None,
            serial_ready=get_value("SerialReady"),
            version_number=get_value("VersionNumber"),
            has_panic=get_value("HasPanic"),
            succeeded=bool(get_value("Succeeded", False)),
            message=str(get_value("Message", "")),
            custom_error_code=int(get_value("CustomErrorCode", -1)),
            model_errors=get_value("ModelErrors"),
        )


@dataclass(frozen=True)
class ComSettingStatus:
    """Status of a COM port configuration setting."""

    setting: int
    is_available: bool
    status: bool
    setting_name: str

    @staticmethod
    def from_json(data: dict[str, Any]) -> ComSettingStatus:
        """Return a ComSettingStatus parsed from an API payload."""
        return ComSettingStatus(
            setting=int(data.get("Setting", 0)),
            is_available=bool(data.get("IsAvailable", False)),
            status=bool(data.get("Status", False)),
            setting_name=str(data.get("SettingName", "")),
        )


@dataclass(frozen=True)
class PartitionStatus:
    """Runtime status for an individual partition."""

    ac_fail: bool
    away_armed: bool
    stay_armed1: bool
    alarmed: bool

    @staticmethod
    def from_json(data: dict[str, Any]) -> PartitionStatus:
        """Return a PartitionStatus parsed from an API payload."""
        return PartitionStatus(
            ac_fail=bool(data.get("AcFail", False)),
            away_armed=bool(data.get("AwayArmed", False)),
            stay_armed1=bool(data.get("StayArmed1", False)),
            alarmed=bool(data.get("Alarmed", False)),
        )


@dataclass(frozen=True)
class ApiFailure:
    """Wrapper for failure payloads where `Succeeded` is false."""

    succeeded: bool
    apn_error_code: int | None
    custom_error_code: int | None
    message: str | None
    level: int | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> ApiFailure:
        """Return an ApiFailure parsed from an API payload."""
        return ApiFailure(
            succeeded=bool(data.get("Succeeded", False)),
            apn_error_code=(
                int(data["ApnErrorCode"]) if data.get("ApnErrorCode") is not None else None
            ),
            custom_error_code=(
                int(data["CustomErrorCode"])
                if data.get("CustomErrorCode") is not None
                else None
            ),
            message=data.get("Message"),
            level=(int(data["Level"]) if data.get("Level") is not None else None),
        )


@dataclass(frozen=True)
class ZoneStatus:
    """Runtime status for an individual zone."""

    is_active: bool
    bypassed: bool

    @staticmethod
    def from_json(data: dict[str, Any]) -> ZoneStatus:
        """Return a ZoneStatus parsed from an API payload."""
        return ZoneStatus(
            is_active=bool(data.get("IsActive", False)),
            bypassed=bool(data.get("Bypassed", False)),
        )


@dataclass(frozen=True)
class AccountProfile:
    """Basic account profile details."""

    first_name: str
    last_name: str
    email: str
    email_confirmed: bool
    phone_number: str | None
    phone_number_confirmed: bool

    @staticmethod
    def from_json(data: dict[str, Any]) -> AccountProfile:
        """Return an AccountProfile parsed from an API payload."""
        return AccountProfile(
            first_name=str(data.get("FirstName", "")),
            last_name=str(data.get("LastName", "")),
            email=str(data.get("Email", "")),
            email_confirmed=bool(data.get("EmailConfirmed", False)),
            phone_number=data.get("PhoneNumber"),
            phone_number_confirmed=bool(data.get("PhoneNumberConfirmed", False)),
        )


@dataclass(frozen=True)
@dataclass(frozen=True)
class ComStatus:
    """Communication module status and metrics."""

    ac_fail: bool
    inputs: list[bool]
    outputs: list[bool]
    system_voltage: str | None
    version_number: str | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> ComStatus:
        """Return a ComStatus parsed from an API payload."""
        return ComStatus(
            ac_fail=bool(data.get("AcFail", False)),
            inputs=list(data.get("Inputs", []) or []),
            outputs=list(data.get("Outputs", []) or []),
            system_voltage=data.get("SystemVoltage"),
            version_number=data.get("VersionNumber"),
        )


@dataclass(frozen=True)
class AppVersionInfo:
    """Application version metadata."""

    live_version: str
    beta_version: str
    force_update_version: str
    terms_version: str | None
    privacy_version: str | None

    @staticmethod
    def from_json(data: dict[str, Any]) -> AppVersionInfo:
        """Return AppVersionInfo parsed from an API payload."""
        return AppVersionInfo(
            live_version=str(data.get("LiveVersion", "")),
            beta_version=str(data.get("BetaVersion", "")),
            force_update_version=str(data.get("ForceUpdateVersion", "")),
            terms_version=(
                str(data["TermsVersion"]) if data.get("TermsVersion") is not None else None
            ),
            privacy_version=(
                str(data["PrivacyVersion"])
                if data.get("PrivacyVersion") is not None
                else None
            ),
        )
