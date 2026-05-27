import unittest
import sys
from pathlib import Path


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    failfast = False
    quiet = False
    filtered = []
    for arg in argv:
        if arg == "--failfast":
            failfast = True
        elif arg == "-q":
            quiet = True
        else:
            filtered.append(arg)

    loader = unittest.TestLoader()
    if filtered:
        suite = unittest.TestSuite()
        for target in filtered:
            target_path = Path(target)
            if target_path.is_dir():
                suite.addTests(loader.discover(str(target_path)))
            elif target_path.suffix == ".py" and target_path.exists():
                suite.addTests(loader.discover(str(target_path.parent), pattern=target_path.name))
            else:
                suite.addTests(loader.loadTestsFromName(target))
    else:
        suite = loader.discover("tests")

    verbosity = 1 if quiet else 2
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=failfast)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
