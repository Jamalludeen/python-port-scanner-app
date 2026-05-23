import socket


def scan_single_port(target: str, port: int) -> (int, bool):
    """Attempt a TCP connection to (target, port). Returns (port, is_open)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex((target, port))
            return (port, result == 0)
    except Exception:
        return (port, False)
