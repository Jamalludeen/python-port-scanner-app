import re
import ipaddress


def is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except Exception:
        return False


def is_valid_hostname(value: str) -> bool:
    if not value:
        return False
    if len(value) > 255:
        return False
    if value[-1] == ".":
        value = value[:-1]
    if value.lower() == "localhost":
        return True
    label_re = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")
    parts = value.split(".")
    for part in parts:
        if not label_re.match(part):
            return False
    return True


def normalize_host(value: str) -> str:
    """Strip optional port from host like example.com:80 -> example.com"""
    if not value:
        return value
    if value.startswith("[") and "]" in value:
        end = value.find("]")
        if end != -1:
            return value[1:end]
    try:
        ipaddress.ip_address(value)
        return value
    except Exception:
        pass
    if value.count(":") == 1:
        return value.rsplit(":", 1)[0]
    return value
