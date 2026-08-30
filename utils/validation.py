import json
import re
from typing import Union

def is_valid_host(host: str) -> bool:
    """Validates host/IP address or domain name."""
    if not host or not host.strip():
        return False
    host = host.strip()

    # Strip protocol if user typed http:// or https://
    if host.startswith("http://"):
        host = host[7:]
    elif host.startswith("https://"):
        host = host[8:]

    # Strip path or port if present
    host = host.split("/")[0].split(":")[0]

    # Simple regex for host IP or domain name
    ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    domain_pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    localhost_pattern = r"^(localhost|esp[a-zA-Z0-9_-]*)$"

    if re.match(ip_pattern, host):
        parts = host.split(".")
        return all(0 <= int(part) <= 255 for part in parts)

    if re.match(domain_pattern, host) or re.match(localhost_pattern, host, re.IGNORECASE):
        return True

    return False


def is_valid_port(port: Union[str, int]) -> bool:
    """Validates port number."""
    try:
        val = int(port)
        return 1 <= val <= 65535
    except (ValueError, TypeError):
        return False


def is_valid_json(text: str) -> bool:
    """Checks if string is valid JSON."""
    if not text or not text.strip():
        return True  # Empty string is valid as empty body/headers
    try:
        json.loads(text)
        return True
    except Exception:
        return False


def validate_config_json(data: dict) -> tuple[bool, str]:
    """Validates structure of imported configuration JSON."""
    if not isinstance(data, dict):
        return False, "Configuration must be a JSON object."

    if "devices" in data and not isinstance(data["devices"], list):
        return False, "'devices' field must be a list."

    if "controls" in data and not isinstance(data["controls"], list):
        return False, "'controls' field must be a list."

    if "categories" in data and not isinstance(data["categories"], list):
        return False, "'categories' field must be a list."

    return True, "Valid configuration structure."
