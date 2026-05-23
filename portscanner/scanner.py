import socket
import concurrent.futures
from datetime import datetime
from typing import Callable, Optional


def scan_single_port(target: str, port: int) -> (int, bool):
    """Attempt a TCP connection to (target, port). Returns (port, is_open)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex((target, port))
            return (port, result == 0)
    except Exception:
        return (port, False)


class PortScanner:
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
    ) -> None:
        total = max(0, end - start + 1)
        completed = 0

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

        # set default socket timeout for connect_ex
        socket.setdefaulttimeout(timeout)

        ports = list(range(start, end + 1))

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(scan_single_port, target, p) for p in ports]

            for fut in concurrent.futures.as_completed(futures):
                if stop_event.is_set():
                    break
                try:
                    port, is_open = fut.result()
                except Exception:
                    continue

                completed += 1
                if result_cb:
                    result_cb(port, is_open)
                if progress_cb:
                    progress_cb(completed, total)

        if stop_event.is_set():
            if info_cb:
                info_cb(f"\n Scan stopped after {completed}/{total} checks.\n", "error")
        else:
            if info_cb:
                info_cb(f"\n Scan completed. Open ports found: (see results)\n", "info")

