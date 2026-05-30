"""Public package exports for the port scanner app."""

__version__ = "0.2.1"


def get_version() -> str:
    return __version__

from .validators import is_valid_ip, is_valid_hostname, normalize_host
from .scanner import scan_single_port, PortScanner
from .utils import export_to_file, copy_to_clipboard
from .gui import PortScannerApp

# Keep the top-level package import friendly for the GUI and scripts.
__all__ = [
    "__version__",
    "get_version",
    "is_valid_ip",
    "is_valid_hostname",
    "normalize_host",
    "scan_single_port",
    "PortScanner",
    "export_to_file",
    "copy_to_clipboard",
    "PortScannerApp",
]
