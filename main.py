from portscanner.gui import PortScannerApp


def main():
    import tkinter as tk

    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
