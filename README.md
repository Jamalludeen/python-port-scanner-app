# Python Port Scanner App

Lightweight GUI port scanner implemented with Tkinter. The codebase is organized
as a small package to separate concerns between scanning logic, validation,
utilities and the GUI.

## Run

Launch the GUI with:

```bash
python main.py
```

Show launcher version:

```bash
python main.py --version
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

You can also target a specific test file while iterating:

```bash
python run_tests.py tests/test_banner.py
```

Useful flags:

```bash
python run_tests.py --failfast
python run_tests.py -q
```

CI is configured via GitHub Actions to run the shared `run_tests.py` entrypoint.

## Banner detection

The GUI offers a "Detect banners" checkbox which will attempt to read a small
banner from any open TCP service discovered during the scan. This is a best-effort
operation with a short timeout and may not work for all services.

Enable it when you want quick service banners (for example HTTP, SMTP, FTP,
or custom text banners) to be displayed alongside results in the UI.

## Development Notes

- The scanner logic exposes a callback-based API (`PortScanner.scan_range`) so
  the GUI can remain responsive; callbacks should marshal UI updates onto the
  Tk main thread (the GUI currently uses `root.after` to do so).
- The GUI title reflects the active target during a scan and the number of open
  ports when the scan completes.
- Very large scan ranges are rejected to reduce accidental overload.
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
