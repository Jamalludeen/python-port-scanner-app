import unittest

from portscanner import APP_NAME, __version__, get_version


class TestPackageExports(unittest.TestCase):
    def test_version_helpers(self):
        self.assertTrue(APP_NAME)
        self.assertEqual(get_version(), __version__)


if __name__ == "__main__":
    unittest.main()
