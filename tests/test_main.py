import unittest

from main import build_parser


class TestMainParser(unittest.TestCase):
    def test_parser_description(self):
        parser = build_parser()
        self.assertIn("Port Scanner", parser.description)


if __name__ == "__main__":
    unittest.main()
