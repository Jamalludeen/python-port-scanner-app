import unittest

from main import build_parser


class TestMainParser(unittest.TestCase):
    def test_parser_description(self):
        parser = build_parser()
        self.assertIn("Port Scanner", parser.description)
        self.assertEqual(parser.prog, "python main.py")
        self.assertIn("check", [action.dest for action in parser._actions])


if __name__ == "__main__":
    unittest.main()
