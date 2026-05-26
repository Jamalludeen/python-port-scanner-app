import unittest
import sys
from pathlib import Path


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    loader = unittest.TestLoader()
    if argv:
        suite = unittest.TestSuite()
        for target in argv:
            target_path = Path(target)
            if target_path.is_dir():
                suite.addTests(loader.discover(str(target_path)))
            elif target_path.suffix == ".py" and target_path.exists():
                suite.addTests(loader.discover(str(target_path.parent), pattern=target_path.name))
            else:
                suite.addTests(loader.loadTestsFromName(target))
    else:
        suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
