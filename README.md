# Python Port Scanner App

Lightweight GUI port scanner implemented with Tkinter. The codebase is organized
as a small package to separate concerns between scanning logic, validation,
utilities and the GUI.

## Run

Launch the GUI with:

```bash
python main.py
```

or the legacy wrapper:

```bash
python portScanner.py
```

## Project Structure

- `portscanner/` - package modules
  - `gui.py` - Tkinter UI (`PortScannerApp`)
  - `scanner.py` - scanning logic (`PortScanner`, `scan_single_port`)
  - `validators.py` - host/IP validation helpers
  - `utils.py` - small helpers (export, clipboard)
- `tests/` - unit tests using Python `unittest`
- `run_tests.py` - convenience test runner
- `main.py` - modern entrypoint
- `portScanner.py` - legacy compatibility wrapper

## Tests

Run the unit tests with:

```bash
python run_tests.py
```

CI is configured via GitHub Actions to run `python -m unittest discover -v`.

## Development Notes

- The scanner logic exposes a callback-based API (`PortScanner.scan_range`) so
  the GUI can remain responsive; callbacks should marshal UI updates onto the
  Tk main thread (the GUI currently uses `root.after` to do so).
- Tests use a local ephemeral server to validate port detection and callback
  behavior.

## License

MIT

# Port Scanner

A simple GUI port scanner built with Tkinter.

Usage:

- Run `python3 portScanner.py`.
- Enter target host/IP and adjust settings.
- Use `Scan`, `Stop`, `Export`, and `Copy` buttons.

Notes:

- This project is for learning and small-scale scanning only. Use responsibly.
