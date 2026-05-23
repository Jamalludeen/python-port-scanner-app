from portscanner.gui import PortScannerApp


if __name__ == "__main__":
    import tkinter as tk

    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()
