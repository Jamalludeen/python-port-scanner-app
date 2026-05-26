import socket
import threading
import unittest
from portscanner.scanner import scan_single_port


class SimpleTCPHandler:
    def __init__(self, conn):
        try:
            conn.recv(1024)
        except Exception:
            pass
        try:
            conn.sendall(b"OK\n")
        except Exception:
            pass
        finally:
            conn.close()


class TestScanner(unittest.TestCase):
    def test_scan_single_port_open_and_closed(self):
        # start a simple server on an ephemeral port
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        host, port = srv.getsockname()

        def server_loop():
            try:
                conn, _ = srv.accept()
                SimpleTCPHandler(conn)
            finally:
                srv.close()

        t = threading.Thread(target=server_loop, daemon=True)
        t.start()

        # open port should be detected
        p, is_open, banner = scan_single_port("127.0.0.1", port)
        self.assertEqual(p, port)
        self.assertTrue(is_open)
        self.assertIsNone(banner)

        # pick a high port likely closed
        p2, is_open2, banner2 = scan_single_port("127.0.0.1", port + 1)
        self.assertEqual(p2, port + 1)
        # closed or filtered, accept False
        self.assertFalse(is_open2)
        self.assertIsNone(banner2)


if __name__ == "__main__":
    unittest.main()
