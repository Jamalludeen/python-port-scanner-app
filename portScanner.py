import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import concurrent.futures
import webbrowser
# COMMIT_MARKER: init-feature-commit-1


class PortScannerApp:
    # Colors
    BG_COLOR = "#1e1e2e"
    FG_COLOR = "#cdd6f4"
    ACCENT_COLOR = "#89b4fa"
    SUCCESS_COLOR = "#a6e3a1"
    ERROR_COLOR = "#f38ba8"
    # Feature defaults (initial setup for custom range/concurrency)
    DEFAULT_START_PORT = 1
    DEFAULT_END_PORT = 1024
    DEFAULT_THREAD_COUNT = 50
    DEFAULT_TIMEOUT = 0.5
    APP_VERSION = "0.2"

    def __init__(self, root):
        self.root = root
        self.root.title(f"Port Scanner v{self.APP_VERSION}")
        self.root.geometry("1300x680")
        self.root.configure(bg=self.BG_COLOR)
        self.root.resizable(True, True)

        self.is_maximized = False
        self.normal_geometry = self.root.geometry()

        self.stop_event = threading.Event()
        self.scan_thread = None
        self.active_futures = set()
        self.submitted_jobs = 0
        self.completed_jobs = 0
        self.open_ports_found = 0

        self.create_widgets()
        # Keyboard shortcuts
        try:
            self.root.bind('<F11>', lambda e: self.toggle_maximize())
            self.root.bind('<Escape>', lambda e: self.toggle_maximize())
        except Exception:
            pass

    # UI adjustment
    def create_widgets(self):
        # Create notebook to host main app and About tab
        self.notebook = ttk.Notebook(self.root)
        self.main_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        self.notebook.add(self.main_frame, text="Main")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Populate main frame
        self.create_title()
        self.create_input_section()
        self.create_results_section()

        # About tab placeholder (will fill in later commits)
        self.about_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        self.notebook.add(self.about_frame, text="About")
        # commit 5: about header
        about_title = tk.Label(
            self.about_frame,
            text="About Port Scanner",
            font=("Segoe UI", 18, "bold"),
            fg=self.ACCENT_COLOR,
            bg=self.BG_COLOR,
        )
        about_title.pack(pady=(20, 6))
        about_version = tk.Label(
            self.about_frame,
            text=f"Version: {self.APP_VERSION}",
            font=("Segoe UI", 11),
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
        )
        about_version.pack()

        about_author = tk.Label(
            self.about_frame,
            text="Author: Your Name",
            font=("Segoe UI", 11),
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
        )
        about_author.pack(pady=(0, 8))

        about_desc = tk.Text(
            self.about_frame,
            height=6,
            width=60,
            bg="#11111b",
            fg=self.FG_COLOR,
            wrap=tk.WORD,
        )
        about_desc.insert(tk.END, "A lightweight GUI port scanner for quick network exploration and learning. Use responsibly.")
        about_desc.config(state=tk.DISABLED)
        about_desc.pack(padx=20, pady=(0, 12))

        license_label = tk.Label(
            self.about_frame,
            text="License:",
            font=("Segoe UI", 12, "bold"),
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
        )
        license_label.pack()

        license_text = tk.Text(
            self.about_frame,
            height=6,
            width=60,
            bg="#11111b",
            fg=self.FG_COLOR,
            wrap=tk.WORD,
        )
        license_text.insert(tk.END, "MIT License - see LICENSE file")
        license_text.config(state=tk.DISABLED)
        license_text.pack(padx=20, pady=(0, 8))

        copy_license_btn = tk.Button(
            self.about_frame,
            text="Copy License",
            font=("Segoe UI", 10, "bold"),
            bg="#6c6cff",
            fg="white",
            command=lambda: self.root.clipboard_append("MIT License - see LICENSE file"),
        )
        copy_license_btn.pack(pady=(0, 12))

    def create_title(self):
        title = tk.Label(
            self.root,
            text="PORT SCANNER",
            font=("Segoe UI", 24, "bold"),
            fg=self.ACCENT_COLOR,
            bg=self.BG_COLOR,
        )
        title.pack(pady=15)
        # commit 3: move title widget into main_frame for tabbed layout
        title.master = self.main_frame

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

        # Port range inputs (initial UI only)
        sp_label = tk.Label(
            frame,
            text="Start Port:",
            font=("Segoe UI", 10),
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
        )
        sp_label.pack(side=tk.LEFT, padx=(12, 5))
        self.start_port_entry = tk.Entry(frame, width=6, font=("Segoe UI", 10))
        self.start_port_entry.insert(0, str(self.DEFAULT_START_PORT))
        self.start_port_entry.pack(side=tk.LEFT, padx=5)
        # Commit 2 note: added start port entry

        ep_label = tk.Label(
            frame,
            text="End Port:",
            font=("Segoe UI", 10),
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
        )
        ep_label.pack(side=tk.LEFT, padx=(6, 5))
        self.end_port_entry = tk.Entry(frame, width=6, font=("Segoe UI", 10))
        self.end_port_entry.insert(0, str(self.DEFAULT_END_PORT))
        self.end_port_entry.pack(side=tk.LEFT, padx=5)

        # Timeout input
        to_label = tk.Label(
            frame,
            text="Timeout(s):",
            font=("Segoe UI", 10),
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
        )
        to_label.pack(side=tk.LEFT, padx=(8, 5))
        self.timeout_entry = tk.Entry(frame, width=6, font=("Segoe UI", 10))
        self.timeout_entry.insert(0, str(self.DEFAULT_TIMEOUT))
        self.timeout_entry.pack(side=tk.LEFT, padx=5)

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

        self.maximize_button = tk.Button(
            frame,
            text="Maximize",
            font=("Segoe UI", 12, "bold"),
            bg=self.SUCCESS_COLOR,
            fg="black",
            command=self.toggle_maximize,
        )
        self.maximize_button.pack(side=tk.LEFT, padx=8)

        # Thread count (initial UI only)
        tc_label = tk.Label(
            frame,
            text="Threads:",
            font=("Segoe UI", 10),
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
        )
        tc_label.pack(side=tk.LEFT, padx=(12, 5))
        self.thread_count_spinbox = tk.Spinbox(
            frame, from_=1, to=500, width=5
        )
        self.thread_count_spinbox.delete(0, tk.END)
        self.thread_count_spinbox.insert(0, str(self.DEFAULT_THREAD_COUNT))
        self.thread_count_spinbox.pack(side=tk.LEFT, padx=5)

        # Toolbar for secondary actions so buttons don't overflow
        toolbar = tk.Frame(self.root, bg=self.BG_COLOR)
        toolbar.pack(fill=tk.X, padx=10, pady=(6, 0))

        self.export_button = tk.Button(
            toolbar,
            text="Export",
            font=("Segoe UI", 10, "bold"),
            bg="#6c6cff",
            fg="white",
            command=self.export_results,
        )
        self.export_button.pack(side=tk.LEFT, padx=8)

        self.copy_button = tk.Button(
            toolbar,
            text="Copy",
            font=("Segoe UI", 10, "bold"),
            bg="#4caf50",
            fg="white",
            command=self.copy_results,
        )
        self.copy_button.pack(side=tk.LEFT, padx=8)

        self.clear_button = tk.Button(
            toolbar,
            text="Clear",
            font=("Segoe UI", 10, "bold"),
            bg="#777777",
            fg="white",
            command=self.clear_results,
        )
        self.clear_button.pack(side=tk.LEFT, padx=8)

        # Banner detection checkbox (UI placeholder)
        self.banner_var = tk.BooleanVar(value=False)
        self.banner_check = tk.Checkbutton(
            toolbar,
            text="Detect banners",
            variable=self.banner_var,
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
            selectcolor=self.BG_COLOR,
        )
        self.banner_check.pack(side=tk.LEFT, padx=8)

        self.help_button = tk.Button(
            toolbar,
            text="Help",
            font=("Segoe UI", 10, "bold"),
            bg="#2196f3",
            fg="white",
            command=self.show_help,
        )
        self.help_button.pack(side=tk.LEFT, padx=8)

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

        # Progress bar (initial UI element)
        self.progress_var = tk.IntVar(value=0)
        progress_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        progress_frame.pack(fill=tk.X, padx=15, pady=(4, 10))
        self.progress_label = tk.Label(
            progress_frame,
            text="Progress:",
            font=("Segoe UI", 10),
            fg=self.FG_COLOR,
            bg=self.BG_COLOR,
        )
        self.progress_label.pack(side=tk.LEFT)
        # Commit 3 note: progress label added
        self.progress = ttk.Progressbar(
            progress_frame, orient=tk.HORIZONTAL, length=400, mode="determinate", variable=self.progress_var
        )
        self.progress.pack(side=tk.LEFT, padx=8)

    # scan control
    def start_scan(self):
        if self.scan_thread and self.scan_thread.is_alive():
            return

        self.stop_event.clear()
        self.active_futures.clear()
        self.submitted_jobs = 0
        self.completed_jobs = 0
        self.open_ports_found = 0
        self.clear_results()

        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.scan_thread = threading.Thread(
            target=self.scan_ports, daemon=True
        )
        self.scan_thread.start()

        # initialize progress for upcoming scan (value and maximum will be set)
        try:
            start, end = self.get_port_range()
            total = max(0, end - start + 1)
            self.progress_var.set(self.completed_jobs)
            self.progress.config(maximum=total)
        except Exception:
            # if UI not fully initialized, ignore for now
            pass

    # Helper getters (initial parsing logic)
    def get_port_range(self):
        try:
            s = int(self.start_port_entry.get())
        except Exception:
            s = self.DEFAULT_START_PORT
        try:
            e = int(self.end_port_entry.get())
        except Exception:
            e = self.DEFAULT_END_PORT
        if s < 1:
            s = 1
        if e < s:
            e = s
        return s, e

    def get_thread_count(self):
        try:
            t = int(self.thread_count_spinbox.get())
        except Exception:
            t = self.DEFAULT_THREAD_COUNT
        if t < 1:
            t = 1
        return t
        # Commit 4 note: basic validation exists for thread count

    def get_timeout(self):
        try:
            v = float(self.timeout_entry.get())
        except Exception:
            v = self.DEFAULT_TIMEOUT
        if v <= 0:
            v = self.DEFAULT_TIMEOUT
        return v

    def scan_single_port(self, target, port):
        if self.stop_event.is_set():
            return (port, False)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex((target, port))
                return (port, result == 0)
        except Exception:
            return (port, False)

    def stop_scan(self):
        self.stop_event.set()
        for future in list(self.active_futures):
            future.cancel()
        self.write_result("\n Scan stopped by user.\n", "error")
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def _record_scan_result(self, port, is_open):
        self.completed_jobs += 1
        self.progress_var.set(self.completed_jobs)
        if is_open:
            self.open_ports_found += 1
            self.write_result(f"✔ Port {port} is OPEN\n", "open")

    def _queue_result_text(self, text, tag=None):
        self.root.after(0, self.write_result, text, tag)

    def _queue_reset_buttons(self):
        self.root.after(0, self.reset_buttons)

    def _queue_error_dialog(self, title, message):
        self.root.after(0, messagebox.showerror, title, message)

    def show_help(self):
        msg = (
            "Port Scanner\n\n"
            "- Enter a target host or IP and press Scan.\n"
            "- Adjust start/end ports, thread count, and timeout.\n"
            "- Use Export/Copy to save results.\n"
            "- F11 toggles maximize.\n"
        )
        messagebox.showinfo("Help", msg)

    def toggle_maximize(self):
        if not self.is_maximized:
            self.normal_geometry = self.root.geometry()
            try:
                self.root.state("zoomed")
            except tk.TclError:
                self.root.attributes("-zoomed", True)
            self.maximize_button.config(text="Restore")
            self.is_maximized = True
        else:
            try:
                self.root.state("normal")
            except tk.TclError:
                self.root.attributes("-zoomed", False)
            if self.normal_geometry:
                self.root.geometry(self.normal_geometry)
            self.maximize_button.config(text="Maximize")
            self.is_maximized = False

    def scan_ports(self):
        target = self.host_entry.get().strip()

        if not target:
            self._queue_error_dialog("Error", "Please enter a hostname or IP address")
            self._queue_reset_buttons()
            return

        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            self._queue_result_text(" Hostname could not be resolved\n", "error")
            self._queue_reset_buttons()
            return

        self._queue_result_text(f"Target: {target}\n")
        self._queue_result_text(f"IP Address: {ip}\n")
        self._queue_result_text(f"Started at: {datetime.now()}\n", "info")
        self._queue_result_text("-" * 40 + "\n")

        socket.setdefaulttimeout(self.get_timeout())

        # Submit scan jobs concurrently using user-selected worker count.
        start_port, end_port = self.get_port_range()
        ports = list(range(start_port, end_port + 1))
        workers = self.get_thread_count()
        self._queue_result_text(f"Workers: {workers}\n", "info")

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            for port in ports:
                if self.stop_event.is_set():
                    break
                future = executor.submit(self.scan_single_port, target, port)
                self.active_futures.add(future)

            self.submitted_jobs = len(self.active_futures)
            self.root.after(0, self.progress.config, {"maximum": max(1, self.submitted_jobs)})

            for future in concurrent.futures.as_completed(self.active_futures):
                if self.stop_event.is_set():
                    break
                try:
                    port, is_open = future.result()
                except Exception:
                    self.active_futures.discard(future)
                    continue
                self.root.after(0, self._record_scan_result, port, is_open)
                self.active_futures.discard(future)

        if self.stop_event.is_set():
            self._queue_result_text(
                f"\n Scan stopped after {self.completed_jobs}/{self.submitted_jobs} checks.\n",
                "error",
            )
        else:
            self._queue_result_text(
                f"\n Scan completed. Open ports found: {self.open_ports_found}\n",
                "info",
            )

        self._queue_reset_buttons()

    def export_results(self):
        content = self.results_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Export", "No results to export")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*")],
            title="Save scan results",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Export", f"Saved results to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def copy_results(self):
        content = self.results_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Copy", "No results to copy")
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Copy", "Results copied to clipboard")
        except Exception as e:
            messagebox.showerror("Copy Error", str(e))

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
