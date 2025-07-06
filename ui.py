import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os
import platform
import subprocess
from pathlib import Path
from tkinterdnd2 import DND_FILES

from processor import ProjectProcessor
from file_utils import format_file_size
from scanner import FileScanner

# --- Constants for UI Design ---
BACKGROUND_COLOR = "#ffffff"
PRIMARY_COLOR = "#4285F4"
PRIMARY_LIGHT_COLOR = "#E8F0FE"
CANCEL_COLOR = "#D93025"
CANCEL_HOVER_COLOR = "#E84C3D"
TEXT_COLOR = "#202124"
TEXT_SECONDARY_COLOR = "#5F6368"
SUCCESS_COLOR = "#34A853"
BUTTON_HOVER_COLOR = "#5A95F5"
BORDER_COLOR = "#DADCE0"
SOFT_BORDER_COLOR = "#E0E0E0"
FONT_FAMILY = "Segoe UI"
FONT_NORMAL = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 11, "bold")
FONT_LARGE_BOLD = (FONT_FAMILY, 16, "bold")


class CodebaseTrackerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Codebase Tracker")
        self.root.geometry("800x600")
        self.root.minsize(700, 550)
        self.root.configure(bg=BACKGROUND_COLOR)

        self.project_path = None
        self.processor = None
        self.output_stats = {}
        
        self.cancel_event = threading.Event()
        self.worker_thread = None

        self._setup_styles()
        self._setup_ui()

    def _setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')

        style.configure("TFrame", background=BACKGROUND_COLOR)
        style.configure("TLabel", background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=FONT_NORMAL)
        style.configure("TLabelframe", background=BACKGROUND_COLOR, bordercolor=SOFT_BORDER_COLOR, relief=tk.SOLID,
                        borderwidth=1)
        style.configure("TLabelframe.Label", background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=FONT_BOLD)

        style.configure("Primary.TButton", background=PRIMARY_COLOR, foreground="white", font=FONT_BOLD, padding=(20, 12), borderwidth=0)
        style.map("Primary.TButton", background=[('active', BUTTON_HOVER_COLOR), ('disabled', '#A0C3FF')], foreground=[('active', 'white')])

        style.configure("Secondary.TButton", background=BACKGROUND_COLOR, foreground=PRIMARY_COLOR, font=FONT_BOLD, padding=(15, 9), borderwidth=1, bordercolor=BORDER_COLOR)
        style.map("Secondary.TButton", background=[('active', PRIMARY_LIGHT_COLOR)], bordercolor=[('active', PRIMARY_COLOR)])

        style.configure("Success.TButton", background=SUCCESS_COLOR, foreground="white", font=FONT_BOLD, padding=(15, 9), borderwidth=0)
        style.map("Success.TButton", background=[('active', '#2E8A47')])
        
        style.configure("Cancel.TButton", background=CANCEL_COLOR, foreground="white", font=FONT_BOLD, padding=(20, 12), borderwidth=0)
        style.map("Cancel.TButton", background=[('active', CANCEL_HOVER_COLOR)])

        style.configure("TProgressbar", thickness=5, background=PRIMARY_COLOR, troughcolor=PRIMARY_LIGHT_COLOR)

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.drop_zone = ttk.Frame(main_frame, style="TLabelframe", relief=tk.SOLID)
        self.drop_zone.pack(fill=tk.X, pady=(0, 20))
        self.drop_zone.pack_propagate(False)
        self.drop_zone.config(height=120)

        drop_label_large = ttk.Label(self.drop_zone, text="Drag & Drop Project Folder Here", font=FONT_LARGE_BOLD, foreground=TEXT_SECONDARY_COLOR)
        drop_label_large.pack(pady=(20, 5), expand=True)

        browse_frame = ttk.Frame(self.drop_zone)
        browse_frame.pack(pady=(0, 20), expand=True)
        ttk.Label(browse_frame, text="or", font=FONT_NORMAL, foreground=TEXT_SECONDARY_COLOR).pack(side=tk.LEFT, padx=10)
        browse_btn = ttk.Button(browse_frame, text="Browse Folder...", style="Secondary.TButton", command=self._browse_folder)
        browse_btn.pack(side=tk.LEFT)

        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self._on_drop)

        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=(0, 20))
        actions_frame.columnconfigure(0, weight=3)
        actions_frame.columnconfigure(1, weight=1)

        self.scan_btn = ttk.Button(actions_frame, text="Scan & Generate", style="Primary.TButton", command=self._scan_project, state=tk.DISABLED)
        self.scan_btn.grid(row=0, column=0, sticky="ew")

        self.cancel_btn = ttk.Button(actions_frame, text="Cancel", style="Cancel.TButton", command=self._on_cancel)
        
        # --- UPDATED: Changed button text and command ---
        self.edit_ignore_btn = ttk.Button(actions_frame, text="Edit track_ignore.txt", style="Secondary.TButton", command=self._edit_track_ignore, state=tk.DISABLED)
        self.edit_ignore_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        status_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Select a project folder to begin.")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, wraplength=700)
        status_label.pack(fill=tk.X, pady=(0, 5))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=1.0)
        self.progress_bar.pack(fill=tk.X, pady=5)

        log_frame = ttk.Frame(status_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=8, bg="#F8F9FA", fg=TEXT_COLOR, relief=tk.SOLID, borderwidth=1, font=FONT_NORMAL)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.results_frame = ttk.LabelFrame(main_frame, text="Result", padding="10")

    def _on_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isdir(path):
            self._set_project_path(path)
        else:
            messagebox.showerror("Error", f"Dropped item is not a valid directory: {path}")

    def _browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select Project Folder")
        if folder_path:
            self._set_project_path(folder_path)

    def _set_project_path(self, path):
        self.project_path = path
        for widget in self.drop_zone.winfo_children():
            widget.destroy()
        path_label = ttk.Label(self.drop_zone, text=f"Project: {path}", font=FONT_BOLD, wraplength=750)
        path_label.pack(pady=40, padx=20, expand=True)

        self.status_var.set(f"Project selected. Ready to scan.")
        self.scan_btn.config(state=tk.NORMAL)
        self.edit_ignore_btn.config(state=tk.NORMAL)
        self._log(f"Project selected: {path}")

    def _on_cancel(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self._log("Cancellation requested by user...")
            self.cancel_event.set()
            self.cancel_btn.config(state=tk.DISABLED, text="Cancelling...")

    def _scan_project(self):
        if not self.project_path:
            messagebox.showerror("Error", "Please select a project folder first.")
            return

        self.processor = ProjectProcessor(self.project_path)
        self.output_stats = {}
        self.cancel_event.clear()

        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Starting scan...")
        self.results_frame.pack_forget()
        
        self.scan_btn.grid_remove()
        self.cancel_btn.grid(row=0, column=0, sticky="ew")
        self.cancel_btn.config(state=tk.NORMAL, text="Cancel")
        self.edit_ignore_btn.config(state=tk.DISABLED)

        self._log(f"Starting to scan project: {self.project_path}")

        self.worker_thread = threading.Thread(target=self._process_project)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def _process_project(self):
        if not self.processor:
            self._log("Error: Processor not initialized. Aborting.")
            self.root.after(0, self._restore_ui_state)
            return

        try:
            success, message, stats = self.processor.run(
                self._scan_callback, self._combine_callback, self.cancel_event
            )
            
            if self.cancel_event.is_set():
                self._update_status("Process cancelled.", 0)
                self._log("The operation was successfully cancelled.")
                return

            if success:
                self.output_stats = stats
                self._update_status("Success! Output file generated.", 1.0)
                self._log(f"Combined {stats.get('text_files', 0)} files. Total characters: {stats.get('total_chars', 0):,}")
                self.root.after(0, self._show_results)
            else:
                self._update_status(f"Error: {message}", 1.0)
                self._log(f"Failed to complete process: {message}")
                messagebox.showerror("Error", f"An error occurred: {message}")
        finally:
            self.root.after(0, self._restore_ui_state)

    def _restore_ui_state(self):
        self.cancel_btn.grid_remove()
        self.scan_btn.grid(row=0, column=0, sticky="ew")
        self.scan_btn.config(state=tk.NORMAL)
        self.edit_ignore_btn.config(state=tk.NORMAL)

    def _scan_callback(self, message, progress):
        self._update_status(message, -1)

    def _combine_callback(self, message, progress):
        self._update_status(message, progress)

    def _update_status(self, message, progress=None):
        def update():
            self.status_var.set(message)
            if progress is not None and progress >= 0:
                self.progress_var.set(progress)
            
            if "Scanning:" in message or "Processing" in message:
                self._log(message, show_timestamp=False)

        self.root.after(0, update)

    def _log(self, message, show_timestamp=True):
        def update():
            if show_timestamp:
                import time
                timestamp = time.strftime("%H:%M:%S")
                self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            else:
                self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        self.root.after(0, update)

    def _show_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        stats = self.output_stats
        if not stats: return

        info_frame = ttk.Frame(self.results_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text=f"Text Files: {stats.get('text_files', 0)}", font=FONT_BOLD).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(info_frame, text=f"Ignored: {stats.get('ignored_items', 0)}", font=FONT_BOLD).pack(side=tk.LEFT, padx=15)
        ttk.Label(info_frame, text=f"Total Chars: {stats.get('total_chars', 0):,}", font=FONT_BOLD).pack(side=tk.LEFT, padx=15)
        if stats.get('errors', 0) > 0:
            ttk.Label(info_frame, text=f"Errors: {stats['errors']}", font=FONT_BOLD, foreground="red").pack(side=tk.LEFT, padx=15)

        btn_frame = ttk.Frame(self.results_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.copy_btn = ttk.Button(btn_frame, text="Copy to Clipboard", style="Success.TButton", command=self._copy_to_clipboard)
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        open_file_btn = ttk.Button(btn_frame, text="Open Output File", style="Secondary.TButton", command=self._open_output_file)
        open_file_btn.pack(side=tk.LEFT, padx=5)

        open_dir_btn = ttk.Button(btn_frame, text="Open Output Directory", style="Secondary.TButton", command=self._open_output_dir)
        open_dir_btn.pack(side=tk.LEFT, padx=5)

        self.results_frame.pack(fill=tk.X, padx=0, pady=(15, 0))

    def _copy_to_clipboard(self):
        if self.processor and self.processor.combiner and os.path.exists(self.processor.combiner.output_file):
            try:
                with open(self.processor.combiner.output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self._log("Content copied to clipboard!")
                original_text = self.copy_btn.cget("text")
                self.copy_btn.config(text="Copied!", state=tk.DISABLED)
                self.root.after(2000, lambda: self.copy_btn.config(text=original_text, state=tk.NORMAL))
            except Exception as e:
                messagebox.showerror("Error", f"Could not copy to clipboard: {e}")
        else:
            messagebox.showerror("Error", "Output file not found. Please generate it first.")

    def _open_path(self, path):
        try:
            if not os.path.exists(path):
                messagebox.showerror("Error", f"Path not found: {path}")
                return
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', path])
            else:
                subprocess.call(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open path: {e}")

    def _open_output_file(self):
        if self.processor and self.processor.combiner and self.processor.combiner.output_file:
            self._open_path(self.processor.combiner.output_file)

    def _open_output_dir(self):
        if self.processor and self.processor.combiner and self.processor.combiner.output_dir:
            self._open_path(self.processor.combiner.output_dir)

    # --- UPDATED: Renamed method and simplified logic ---
    def _edit_track_ignore(self):
        """Opens the track_ignore.txt file for editing."""
        if not self.project_path:
            messagebox.showerror("Error", "Please select a project folder first")
            return
        
        # The IgnoreRules class now handles the creation of the file automatically
        # upon initialization. We just need to get the path and open it.
        scanner = FileScanner(self.project_path)
        track_ignore_path = scanner.ignore_rules.get_track_ignore_path()
        
        self._open_path(track_ignore_path)
