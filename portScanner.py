import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


class PortScannerApp:
    # Colors
    BG_COLOR = "#1e1e2e"
    FG_COLOR = "#cdd6f4"
    ACCENT_COLOR = "#89b4fa"
    SUCCESS_COLOR = "#a6e3a1"
    ERROR_COLOR = "#f38ba8"

    def __init__(self, root):
        self.root = root
        self.root.title("Port Scanner")
        self.root.geometry("700x500")
        self.root.configure(bg=self.BG_COLOR)
        self.root.resizable(False, False)

        self.stop_event = threading.Event()
        self.scan_thread = None

        self.create_widgets()

    # UI adjustment
    def create_widgets(self):
        self.create_title()
        self.create_input_section()
        self.create_results_section()

    def create_title(self):
        title = tk.Label(
            self.root,
            text="PORT SCANNER",
            font=("Segoe UI", 24, "bold"),
            fg=self.ACCENT_COLOR,
            bg=self.BG_COLOR,
        )
        title.pack(pady=15)

    def create_input_section(self):
        frame = tk.Frame(self.root, bg=self.BG_COLOR)
        frame.pack(pady=10)

        label = tk.Label(
            frame,
            text="Target Host/IP:",
            font=("Segoe UI", 12),
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
        )
        label.pack(side=tk.LEFT, padx=5)

        self.host_entry = tk.Entry(frame, width=30, font=("Segoe UI", 12))
        self.host_entry.pack(side=tk.LEFT, padx=5)

        self.scan_button = tk.Button(
            frame,
            text="Scan",
            font=("Segoe UI", 12, "bold"),
            bg=self.ACCENT_COLOR,
            fg="black",
            command=self.start_scan,
        )
        self.scan_button.pack(side=tk.LEFT, padx=8)

        self.stop_button = tk.Button(
            frame,
            text="Stop",
            font=("Segoe UI", 12, "bold"),
            bg=self.ERROR_COLOR,
            fg="black",
            state=tk.DISABLED,
            command=self.stop_scan,
        )
        self.stop_button.pack(side=tk.LEFT, padx=8)

    def create_results_section(self):
        frame = tk.Frame(self.root, bg=self.BG_COLOR)
        frame.pack(pady=15, fill=tk.BOTH, expand=True)

        self.results_box = tk.Text(
            frame,
            bg="#11111b",
            fg=self.FG_COLOR,
            font=("Consolas", 11),
            wrap=tk.WORD,
        )
        self.results_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, command=self.results_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_box.config(yscrollcommand=scrollbar.set)

        self.results_box.tag_config("open", foreground=self.SUCCESS_COLOR)
        self.results_box.tag_config("error", foreground=self.ERROR_COLOR)
        self.results_box.tag_config("info", foreground=self.ACCENT_COLOR)

    # scan control
    def start_scan(self):
        if self.scan_thread and self.scan_thread.is_alive():
            return

        self.stop_event.clear()
        self.clear_results()

        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.scan_thread = threading.Thread(
            target=self.scan_ports, daemon=True
        )
        self.scan_thread.start()

    def stop_scan(self):
        self.stop_event.set()
        self.write_result("\n Scan stopped by user.\n", "error")
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def scan_ports(self):
        target = self.host_entry.get().strip()

        if not target:
            messagebox.showerror("Error", "Please enter a hostname or IP address")
            self.reset_buttons()
            return

        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            self.write_result(" Hostname could not be resolved\n", "error")
            self.reset_buttons()
            return

        self.write_result(f"Target: {target}\n")
        self.write_result(f"IP Address: {ip}\n")
        self.write_result(f"Started at: {datetime.now()}\n", "info")
        self.write_result("-" * 40 + "\n")

        socket.setdefaulttimeout(0.5)

        for port in range(1, 1025):
            if self.stop_event.is_set():
                break

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = s.connect_ex((target, port))
                if result == 0:
                    self.write_result(f"✔ Port {port} is OPEN\n", "open")
                s.close()
            except Exception:
                pass

        if not self.stop_event.is_set():
            self.write_result("\n Scan completed.\n", "info")

        self.reset_buttons()

    # HELPERS
    def clear_results(self):
        self.results_box.delete("1.0", tk.END)

    def write_result(self, text, tag=None):
        self.results_box.insert(tk.END, text, tag)
        self.results_box.see(tk.END)

    def reset_buttons(self):
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()

