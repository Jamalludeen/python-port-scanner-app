import unittest
from portscanner.validators import is_valid_ip, is_valid_hostname, normalize_host


class TestValidators(unittest.TestCase):
    def test_is_valid_ip(self):
        self.assertTrue(is_valid_ip("127.0.0.1"))
        self.assertFalse(is_valid_ip("999.999.999.999"))

    def test_is_valid_hostname(self):
        self.assertTrue(is_valid_hostname("localhost"))
        self.assertTrue(is_valid_hostname("example.com"))
        self.assertFalse(is_valid_hostname("-bad-host"))

    def test_normalize_host(self):
        self.assertEqual(normalize_host("example.com:80"), "example.com")
        self.assertEqual(normalize_host("[::1]:8080"), "::1")
        self.assertEqual(normalize_host("::1"), "::1")


if __name__ == "__main__":
    unittest.main()
