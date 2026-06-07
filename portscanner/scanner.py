import socket
import concurrent.futures
from datetime import datetime
from typing import Callable, Optional, Tuple

DEFAULT_CONNECT_TIMEOUT = 0.5


def scan_single_port(
    target: str,
    port: int,
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
    banner: bool = False,
    banner_timeout: float = 0.5,
) -> Tuple[int, bool, Optional[str]]:
    """Attempt a TCP connection to (target, port).

    Returns a tuple (port, is_open, banner_text).
    If `banner` is True and the port is open, the function will try to read
    a small banner from the remote side using a short timeout.
    """
    banner_text = None
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(connect_timeout)
            result = sock.connect_ex((target, port))
            is_open = (result == 0)
            if is_open and banner:
                try:
                    # try to receive a short banner without blocking too long
                    sock.settimeout(banner_timeout)
                    data = sock.recv(1024)
                    if data:
                        try:
                            banner_text = data.decode('utf-8', errors='replace').strip()
                        except Exception:
                            banner_text = None
                except Exception:
                    banner_text = None
            return (port, is_open, banner_text)
    except Exception:
        return (port, False, None)


class PortScanner:
    MIN_TIMEOUT = 0.05
    MAX_PORTS_PER_SCAN = 4096
    # Keep accidental scans bounded so the GUI stays responsive.
    RANGE_LIMIT_MESSAGE = " Scan aborted: range exceeds {limit} ports.\n"

    """Controller for scanning port ranges with callbacks.

    Methods:
        scan_range(target, start, end, workers, timeout, stop_event,
                   result_cb, progress_cb, info_cb)
    Callbacks are called from worker threads; GUI should marshal to main thread.
    """

    def scan_range(
        self,
        target: str,
        start: int,
        end: int,
        workers: int,
        timeout: float,
        stop_event,
        result_cb: Optional[Callable[[int, bool], None]] = None,
        progress_cb: Optional[Callable[[int, int], None]] = None,
        info_cb: Optional[Callable[[str, Optional[str]], None]] = None,
        banner: bool = False,
        banner_timeout: float = 0.5,
    ) -> None:
        workers = max(1, int(workers))
        timeout = max(self.MIN_TIMEOUT, float(timeout))
        banner_timeout = max(self.MIN_TIMEOUT, float(banner_timeout))

        if end < start:
            if info_cb:
                info_cb(" Scan completed: empty port range.\n", "info")
            return

        if (end - start + 1) > self.MAX_PORTS_PER_SCAN:
            if info_cb:
                info_cb(self.RANGE_LIMIT_MESSAGE.format(limit=self.MAX_PORTS_PER_SCAN), "error")
            return

        started_at = datetime.now()
        total = max(0, end - start + 1)
        completed = 0
        open_ports = 0

        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            if info_cb:
                info_cb(" Hostname could not be resolved\n", "error")
            return

        if info_cb:
            info_cb(f"Target: {target}\n")
            info_cb(f"IP Address: {ip}\n")
            info_cb(f"Started at: {datetime.now()}\n", "info")
            info_cb("-" * 40 + "\n")
            info_cb(f"Workers: {workers}\n", "info")

        ports = list(range(start, end + 1))

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(scan_single_port, target, p, timeout, banner, banner_timeout) for p in ports]

            for fut in concurrent.futures.as_completed(futures):
                if stop_event.is_set():
                    break
                try:
                    # fut.result may now return (port, is_open, banner)
                    res = fut.result()
                    if isinstance(res, tuple) and len(res) == 3:
                        port, is_open, banner_text = res
                    else:
                        port, is_open = res
                        banner_text = None
                except Exception:
                    continue

                completed += 1
                if is_open:
                    open_ports += 1
                if result_cb:
                    # result_cb signature: (port, is_open, banner_text)
                    try:
                        result_cb(port, is_open, banner_text)
                    except TypeError:
                        # backward compatibility: accept result_cb(port, is_open)
                        result_cb(port, is_open)
                if progress_cb:
                    progress_cb(completed, total)

        if stop_event.is_set():
            if info_cb:
                info_cb(f"\n Scan stopped after {completed}/{total} checks.\n", "error")
        else:
            if info_cb:
                elapsed = (datetime.now() - started_at).total_seconds()
                info_cb(f"\n Scan completed in {elapsed:.2f}s. Open ports found: {open_ports}\n", "info")

