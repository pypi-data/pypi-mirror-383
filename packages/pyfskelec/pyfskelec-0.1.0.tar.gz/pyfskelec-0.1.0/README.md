# pyfskelec

Minimal Python client for ArmME / MiFalcon alarm systems, reverse-engineered from the official mobile application. It is designed for experimentation, diagnostics, and integrations such as Home Assistant custom components.

> ⚠️ This project is not affiliated with or endorsed by the ArmME / MiFalcon vendor. Use at your own risk and abide by the terms of service of the cloud API.

---

## Features

- Password and refresh-token authentication against the `/Token` endpoint
- Device discovery: list devices, fetch capabilities, properties, and company branding
- Connection control: open/close session, ping the panel, retrieve COM status
- Alarm-system polling helpers: partitions, zones, and COM settings status
- Push registration helper
- Typed data models with dataclass parsing utilities
- CLI (`python -m pyfskelec`) to quickly inspect accounts and panels

## Installation

```bash
pip install pyfskelec
```

Or install from source:

```bash
git clone https://github.com/your-user/pyfskelec.git
cd pyfskelec
pip install -e .
```

## Quick Start

### Library usage

```python
from pyfskelec import ArmMEClient, new_session_id

client = ArmMEClient(client_secret="your_secret")
client.login_password("email@example.com", "password")

profile = client.get_account_profile()
print(profile.email)

for device in client.list_devices():
    print(device.name, device.serial_no)

# Poll a panel
device = client.list_devices()[0]
session_id = new_session_id()
open_info = client.open_connection(device.device_id, device.device_type_id, "1234")
print(open_info.version_number)

zones = client.zone_status(device.device_type_id, device.device_id, "1234", 1, session_id=session_id)
print(zones)

client.close_connection(device.device_id)
```

### Command-line helper

```bash
python -m pyfskelec email@example.com password [serial] [panel_code]
```

- Prints account profile and devices
- If `panel_code` is provided, opens the connection briefly and logs status
- Use `--verbose` for debug logging

Run `python -m pyfskelec --help` for more options.

## Development

```bash
pip install -r requirements_test.txt
python -m ruff check pyfskelec
python -m mypy pyfskelec
pytest
```

## Roadmap

- Wiring for arming/disarming actions
- Historical event retrieval
- Push notification polling
- Automated test coverage for the CLI

## Contributing

Pull requests are welcome! Please:

1. Fork the repository and create a feature branch
2. Add tests or fixtures when possible
3. Run linting and typing checks
4. Submit a PR with a clear description

By contributing you agree to license your work under the project’s Apache 2.0 license.

## License

GPL-3.0 license – see [LICENSE.md](LICENSE.md).