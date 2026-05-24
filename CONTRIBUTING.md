# Contributing

Thanks for contributing! A few guidelines for making changes:

- Keep UI code in `portscanner/gui.py` and scanning/IO in `portscanner/scanner.py`.
- Add unit tests under `tests/` using the standard `unittest` framework.
- Run tests locally with `python run_tests.py` and ensure they pass before pushing.
- CI runs on GitHub Actions and will execute `python -m unittest discover -v`.

When adding features, prefer small, focused commits and update `README.md`
with any new usage or configuration instructions.
