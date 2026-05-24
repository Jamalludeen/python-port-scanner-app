import socket
import threading
import unittest
from portscanner.scanner import scan_single_port


class BannerServer:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(("127.0.0.1", 0))
        self.s.listen(1)
        self.host, self.port = self.s.getsockname()

    def start_once(self, banner_text=b"HELLO\n"):
        def run():
            conn, _ = self.s.accept()
            try:
                conn.sendall(banner_text)
            finally:
                conn.close()
                self.s.close()

        t = threading.Thread(target=run, daemon=True)
        t.start()
        return t


class TestBannerDetection(unittest.TestCase):
    def test_scan_single_port_banner(self):
        srv = BannerServer()
        srv.start_once(b"MyBanner v1.2\n")

        p, is_open, banner = scan_single_port("127.0.0.1", srv.port, banner=True, banner_timeout=1.0)
        self.assertEqual(p, srv.port)
        self.assertTrue(is_open)
        self.assertIsNotNone(banner)
        self.assertIn("MyBanner", banner)


if __name__ == "__main__":
    unittest.main()
