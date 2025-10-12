"""Minimal client for https://api.srnservices.net (ArmME / MiFalcon).

Features:
* OAuth /Token (password + refresh)
* Mirrors app headers (User-Agent: Dart/3.2 (dart:io), Authorization: Bearer …)
* Device listing, capabilities, properties, company info
* Push registration
* Device connection open/close, ping
* Partition and zone status helpers
"""

from __future__ import annotations

from collections.abc import Iterable
import json
import logging
import time
from typing import Any
import uuid

import requests

from .const import (
    DEFAULT_APP_VERSION,
    DEFAULT_BASE_URL,
    DEFAULT_CLIENT_ID,
    DEFAULT_CLIENT_SECRET,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
)
from .exceptions import ArmMEAuthError, ArmMERequestError
from .models import (
    AccountProfile,
    ApiFailure,
    AppVersionInfo,
    CompanyInfo,
    ComSettingStatus,
    ComStatus,
    DeviceCapability,
    DeviceOpenInfo,
    DeviceProperties,
    DeviceSummary,
    OperationResult,
    PartitionStatus,
    PingResult,
    TokenBundle,
    ZoneStatus,
)

logger = logging.getLogger(__name__)


def new_session_id() -> str:
    """Return a UUIDv1 string matching the mobile app's session id format."""
    return str(uuid.uuid1())


class ArmMEClient:
    """Client for https://api.srnservices.net using OWIN /Token.

    Mirrors the app's headers:
      User-Agent: Dart/3.2 (dart:io)
      Authorization: Bearer <access_token>
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        client_id: str = DEFAULT_CLIENT_ID,
        client_secret: str = DEFAULT_CLIENT_SECRET,
        session: requests.Session | None = None,
        user_agent: str | None = DEFAULT_USER_AGENT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the ArmME client session."""
        self.base = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.s = session or requests.Session()
        self.timeout = timeout

        if user_agent:
            self.s.headers["User-Agent"] = user_agent
        self.s.headers.setdefault("Accept", "application/json")

        self._token: TokenBundle | None = None
        self._exp_ts: float = 0.0

    # ---------- Auth ----------

    def login_password(
        self,
        username: str,
        password: str,
        *,
        scope: str | None = None,
    ) -> TokenBundle:
        """POST /Token with grant_type=password (+ client_id/client_secret)."""
        url = f"{self.base}/Token"
        form = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if scope:
            form["scope"] = scope

        response = self.s.post(url, data=form, timeout=self.timeout)
        self._ensure_status(response, "POST", url)

        token_bundle = TokenBundle.from_json(response.json())
        self._install_token(token_bundle)
        return token_bundle

    def refresh(self) -> TokenBundle:
        """POST /Token with grant_type=refresh_token."""
        if not self._token or not self._token.refresh_token:
            raise ArmMEAuthError("No refresh_token available")

        url = f"{self.base}/Token"
        form = {
            "grant_type": "refresh_token",
            "refresh_token": self._token.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = self.s.post(url, data=form, timeout=self.timeout)
        self._ensure_status(response, "POST", url)

        token_bundle = TokenBundle.from_json(response.json())
        if not token_bundle.refresh_token and self._token.refresh_token:
            token_bundle.refresh_token = self._token.refresh_token
        self._install_token(token_bundle)
        return token_bundle

    def _install_token(self, bundle: TokenBundle) -> None:
        self._token = bundle
        self.s.headers["Authorization"] = f"Bearer {bundle.access_token}"
        self._exp_ts = time.time() + int(bundle.expires_in) - 30

    def _ensure_token(self) -> None:
        if not self._token:
            raise ArmMEAuthError("Not authenticated")
        if time.time() >= self._exp_ts and self._token.refresh_token:
            self.refresh()

    # ---------- HTTP helpers ----------

    def _url(self, path: str) -> str:
        return path if path.startswith("http") else f"{self.base}/{path.lstrip('/')}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        retry_on_401: bool = True,
        **kwargs: Any,
    ) -> requests.Response:
        """Perform an authenticated request with optional 401 retry."""
        self._ensure_token()
        response = self.s.request(method, self._url(path), timeout=self.timeout, **kwargs)
        if (
            response.status_code == 401
            and retry_on_401
            and self._token
            and self._token.refresh_token
        ):
            logger.debug("401 encountered, attempting token refresh")
            self.refresh()
            response = self.s.request(
                method,
                self._url(path),
                timeout=self.timeout,
                **kwargs,
            )

        self._ensure_status(response, method, path)
        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        """Issue a GET request using the authenticated session."""
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        """Issue a POST request using the authenticated session."""
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        """Issue a PUT request using the authenticated session."""
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        """Issue a DELETE request using the authenticated session."""
        return self._request("DELETE", path, **kwargs)

    def get_json(self, path: str, **kwargs: Any) -> Any:
        """Return JSON decoded response for a GET request."""
        return self.get(path, **kwargs).json()

    def post_json(self, path: str, payload: Any, **kwargs: Any) -> Any:
        """POST JSON payload and return decoded response."""
        headers = kwargs.pop("headers", {})
        headers = {"Content-Type": "application/json", **headers}
        return self.post(path, json=payload, headers=headers, **kwargs).json()

    def _ensure_status(
        self,
        response: requests.Response,
        method: str,
        path: str,
    ) -> None:
        """Ensure the response status is 200; raise on error."""
        if response.status_code == 200:
            return

        detail = self._format_error_detail(response)
        if response.status_code == 409:
            raise ArmMERequestError(
                f"{method.upper()} {path} -> 409 Conflict: {detail}"
            )

        raise ArmMERequestError(f"{method.upper()} {path} -> {response.status_code}: {detail}")

    @staticmethod
    def _format_error_detail(response: requests.Response) -> str:
        """Extract a human-readable error description from a response."""
        try:
            payload = response.json()
        except ValueError:
            text = response.text.strip()
            return text or "<empty response>"

        if isinstance(payload, dict):
            for key in ("Message", "message", "error_description", "error", "detail"):
                value = payload.get(key)
                if value:
                    return str(value)
            return json.dumps(payload, ensure_ascii=False)

        return json.dumps(payload, ensure_ascii=False)

    # ---------- Domain: devices & config ----------

    def list_devices(self) -> list[DeviceSummary]:
        """GET /api/mydevices/list/{client_id} and parse the results."""
        data = self.get_json(f"/api/mydevices/list/{self.client_id}")
        if not isinstance(data, list):
            raise ArmMERequestError(f"Unexpected device list payload: {data!r}")
        return [DeviceSummary.from_json(item) for item in data]

    def _find_device(self, predicate: Any) -> DeviceSummary | None:
        for device in self.list_devices():
            if predicate(device):
                return device
        return None

    def get_device_by_serial(self, serial_no: str) -> DeviceSummary | None:
        """Return the first device matching the provided serial number."""
        serial = str(serial_no)
        return self._find_device(lambda device: device.serial_no == serial)

    def get_device_by_id(self, device_id: int) -> DeviceSummary | None:
        """Return the first device matching the provided numeric identifier."""
        ident = int(device_id)
        return self._find_device(lambda device: device.device_id == ident)

    def get_device_capability(self, device_id: int) -> DeviceCapability:
        """GET /api/AlarmPanelConfig/GetDeviceCapability/{client_id}/{device_id}."""
        data = self.get_json(
            f"/api/AlarmPanelConfig/GetDeviceCapability/{self.client_id}/{int(device_id)}"
        )
        return DeviceCapability.from_json(data)

    def get_device_properties(self, device_id: int) -> DeviceProperties:
        """GET /api/AlarmPanelConfig/GetDeviceProperties and parse DeviceConfig."""
        data = self.get_json(
            f"/api/AlarmPanelConfig/GetDeviceProperties/{self.client_id}/{int(device_id)}"
        )
        return DeviceProperties.from_json(data)

    def get_company_info_for_device(self, device_id: int) -> CompanyInfo:
        """GET /api/company/GetCompanyInfoForDevice/{device_id}."""
        data = self.get_json(f"/api/company/GetCompanyInfoForDevice/{int(device_id)}")
        return CompanyInfo.from_json(data)

    def get_account_profile(self) -> AccountProfile:
        """GET /api/Account/Profile for the authenticated user."""
        data = self.get_json("/api/Account/Profile")
        if not isinstance(data, dict):
            raise ArmMERequestError(f"Unexpected account profile payload: {data!r}")
        return AccountProfile.from_json(data)

    def get_com_status(
        self,
        device_type_id: int,
        device_id: int,
        panel_code: str,
        *,
        rep: int = 0,
        session_id: str,
    ) -> ComStatus:
        """GET /api/AlarmSystem/ComStatus for current session."""
        path = (
            f"/api/AlarmSystem/ComStatus/{int(device_type_id)}/{int(device_id)}/"
            f"{self.client_id}/{int(rep)}/{session_id}"
        )
        data = self.get_json(path)
        if not isinstance(data, dict):
            raise ArmMERequestError(f"Unexpected ComStatus payload: {data!r}")
        return ComStatus.from_json(data)

    def get_app_versions(self) -> AppVersionInfo:
        """GET /api/Maintenance/AllAppVersions/{client_id}."""
        path = f"/api/Maintenance/AllAppVersions/{self.client_id}"
        data = self.get_json(path)
        if not isinstance(data, dict):
            raise ArmMERequestError(f"Unexpected maintenance payload: {data!r}")
        return AppVersionInfo.from_json(data)

    # ---------- Domain: push ----------

    def register_phone(self, mobile_device_id: str, fcm_token: str) -> OperationResult:
        """POST /api/Push/RegisterPhone with MobileDeviceId, Token, MobileClientId."""
        payload = {
            "MobileDeviceId": mobile_device_id,
            "Token": fcm_token,
            "MobileClientId": self.client_id,
        }
        data = self.post_json("/api/Push/RegisterPhone", payload=payload)
        return OperationResult.from_json(data)

    # ---------- Domain: device connection ----------

    def ping_device(self, device_id: int) -> PingResult:
        """GET /api/DeviceConnection/ping/{device_id}."""
        data = self.get_json(f"/api/DeviceConnection/ping/{int(device_id)}")
        return PingResult.from_json(data)

    def open_connection(
        self,
        device_id: int,
        device_type_id: int,
        panel_code: str,
        *,
        app_version: str | None = None,
        longitude: float | None = None,
        latitude: float | None = None,
        accuracy: float | None = None,
    ) -> DeviceOpenInfo:
        """POST /api/DeviceConnection/Open with optional version and geo metadata."""
        payload: dict[str, Any] = {
            "deviceId": int(device_id),
            "deviceTypeId": int(device_type_id),
            "PanelCode": panel_code,
            "MobileClientId": self.client_id,
        }
        if app_version:
            payload["data"] = json.dumps({"appVersion": app_version})
        if longitude is not None:
            payload["Longitude"] = float(longitude)
        if latitude is not None:
            payload["Latitude"] = float(latitude)
        if accuracy is not None:
            payload["Accuracy"] = float(accuracy)

        data = self.post_json("/api/DeviceConnection/Open", payload=payload)
        return DeviceOpenInfo.from_json(data)

    def close_connection(self, device_id: int) -> OperationResult:
        """POST /api/DeviceConnection/Close."""
        payload = {
            "deviceId": int(device_id),
            "MobileClientId": self.client_id,
        }
        data = self.post_json("/api/DeviceConnection/Close", payload=payload)
        return OperationResult.from_json(data)

    # ---------- Domain: alarm system ----------

    def com_settings_status(
        self,
        device_id: int,
        device_type_id: int,
        *,
        session_id: str,
        rep: int = 0,
    ) -> list[ComSettingStatus]:
        """POST /api/AlarmSystem/ComSettingsStatus."""
        payload = {
            "DeviceId": int(device_id),
            "DeviceTypeId": int(device_type_id),
            "MobileClientId": self.client_id,
            "Rep": int(rep),
            "SessionId": session_id,
        }
        data = self.post_json("/api/AlarmSystem/ComSettingsStatus", payload=payload)
        if not isinstance(data, list):
            raise ArmMERequestError(
                f"Unexpected payload for ComSettingsStatus: {data!r}"
            )
        return [ComSettingStatus.from_json(item) for item in data]

    def partition_status_all(
        self,
        device_type_id: int,
        device_id: int,
        panel_code: str,
        *,
        session_id: str,
        rep: int = 0,
    ) -> list[PartitionStatus] | ApiFailure:
        """GET partition status for all partitions or return the failure payload."""
        path = (
            f"/api/AlarmSystem/PartitionStatusAll/"
            f"{int(device_type_id)}/{int(device_id)}/{panel_code}/"
            f"{self.client_id}/{int(rep)}/{session_id}"
        )
        data = self.get_json(path)
        if isinstance(data, list):
            return [PartitionStatus.from_json(item) for item in data]
        return ApiFailure.from_json(data)

    def zone_status(
        self,
        device_type_id: int,
        device_id: int,
        panel_code: str,
        partition: int,
        *,
        session_id: str,
        rep: int = 0,
    ) -> list[ZoneStatus] | ApiFailure:
        """GET zone status or return the failure payload when the API reports error."""
        path = (
            f"/api/AlarmSystem/ZoneStatus/{int(device_type_id)}/{int(device_id)}/"
            f"{panel_code}/{int(partition)}/{self.client_id}/{int(rep)}/{session_id}"
        )
        data = self.get_json(path)
        if isinstance(data, list):
            return [ZoneStatus.from_json(item) for item in data]
        return ApiFailure.from_json(data)

    # ---------- Convenience helpers ----------

    def start_session(
        self,
        device: DeviceSummary,
        panel_code: str,
        *,
        app_version: str = DEFAULT_APP_VERSION,
        longitude: float | None = None,
        latitude: float | None = None,
        accuracy: float | None = None,
        session_id: str | None = None,
    ) -> tuple[str, DeviceOpenInfo]:
        """Open a connection and return a fresh session id with open info."""
        sid = session_id or new_session_id()
        open_info = self.open_connection(
            device_id=device.device_id,
            device_type_id=device.device_type_id,
            panel_code=panel_code,
            app_version=app_version,
            longitude=longitude,
            latitude=latitude,
            accuracy=accuracy,
        )
        return sid, open_info


    @staticmethod
    def map_zone_status_to_names(
        zone_status: Iterable[ZoneStatus],
        zone_names: dict[str, str],
    ) -> list[tuple[str, bool, bool]]:
        """Return list of (friendly_name, is_active, bypassed) tuples for zones."""
        named_status: list[tuple[str, bool, bool]] = []
        for index, status in enumerate(zone_status, start=1):
            name = zone_names.get(str(index), f"Zone {index}")
            named_status.append((name, status.is_active, status.bypassed))
        return named_status

    def poll_loop(
        self,
        device: DeviceSummary,
        panel_code: str,
        *,
        partition: int = 1,
        app_version: str = DEFAULT_APP_VERSION,
        session_id: str | None = None,
    ) -> None:
        """Minimal polling example: open → fetch → print → close."""
        logger.info("Opening connection for device %s", device.device_id)
        session_id, _ = self.start_session(
            device,
            panel_code,
            app_version=app_version,
            session_id=session_id,
        )

        props = self.get_device_properties(device.device_id)
        zone_names = props.names.zone_names

        zones = self.zone_status(
            device.device_type_id,
            device.device_id,
            panel_code,
            partition,
            session_id=session_id,
        )
        if isinstance(zones, list):
            for name, active, bypassed in self.map_zone_status_to_names(zones, zone_names):
                logger.info("%s: active=%s bypassed=%s", name, active, bypassed)
        else:
            logger.warning("Zone status failure detected, attempting reconnection")
            self.close_connection(device.device_id)
            session_id, _ = self.start_session(
                device,
                panel_code,
                app_version=app_version,
            )

        com_status = self.get_com_status(
            device.device_type_id,
            device.device_id,
            panel_code,
            session_id=session_id,
        )
        logger.info(
            "Com status: ac_fail=%s voltage=%s version=%s inputs=%s outputs=%s",
            com_status.ac_fail,
            com_status.system_voltage,
            com_status.version_number,
            com_status.inputs,
            com_status.outputs,
        )

        partitions = self.partition_status_all(
            device.device_type_id,
            device.device_id,
            panel_code,
            session_id=session_id,
        )
        if isinstance(partitions, list):
            for idx, partition_status in enumerate(partitions, start=1):
                logger.info(
                    "Partition %s: away=%s stay=%s alarmed=%s",
                    idx,
                    partition_status.away_armed,
                    partition_status.stay_armed1,
                    partition_status.alarmed,
                )

        logger.info("Closing connection for device %s", device.device_id)
        self.close_connection(device.device_id)
