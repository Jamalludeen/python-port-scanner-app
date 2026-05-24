import socket
import threading
import unittest
from portscanner.scanner import PortScanner


class TestPortScanner(unittest.TestCase):
    def test_scan_range_callbacks(self):
        # start a simple server to ensure at least one open port
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        host, port = srv.getsockname()

        def server_loop():
            try:
                conn, _ = srv.accept()
                try:
                    conn.recv(1024)
                finally:
                    conn.close()
            finally:
                srv.close()

        t = threading.Thread(target=server_loop, daemon=True)
        t.start()

        scanner = PortScanner()
        results = []
        progress = []
        infos = []

        def result_cb(port, is_open):
            results.append((port, is_open))

        def progress_cb(completed, total):
            progress.append((completed, total))

        def info_cb(text, tag=None):
            infos.append((text, tag))

        stop_event = threading.Event()
        scanner.scan_range("127.0.0.1", port, port + 1, workers=2, timeout=0.5, stop_event=stop_event, result_cb=result_cb, progress_cb=progress_cb, info_cb=info_cb)

        # ensure callbacks received
        self.assertTrue(len(results) >= 1)
        self.assertTrue(len(progress) >= 1)
        self.assertTrue(any("Workers" in (t[0] or "") for t in infos))


if __name__ == "__main__":
    unittest.main()
