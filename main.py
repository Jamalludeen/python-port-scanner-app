import argparse

from portscanner.gui import PortScannerApp
from portscanner import __version__


def main():
    import tkinter as tk

    parser = argparse.ArgumentParser(description="Launch the Port Scanner GUI")
    parser.add_argument("--version", action="version", version=f"python-port-scanner-app {__version__}")
    parser.parse_args()

    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
