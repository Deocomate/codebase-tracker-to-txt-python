import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os
import platform
import subprocess
from pathlib import Path
from tkinterdnd2 import DND_FILES

from scanner import FileScanner
from combiner import FileCombiner
from file_utils import format_file_size

# --- Constants for UI Design ---
BACKGROUND_COLOR = "#ffffff"
PRIMARY_COLOR = "#4285F4"
PRIMARY_LIGHT_COLOR = "#E8F0FE"
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
        self.scanner = None
        self.combiner = None
        self.output_stats = {}

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

        style.configure("Primary.TButton",
                        background=PRIMARY_COLOR,
                        foreground="white",
                        font=FONT_BOLD,
                        padding=(20, 12),
                        borderwidth=0)
        style.map("Primary.TButton",
                  background=[('active', BUTTON_HOVER_COLOR)],
                  foreground=[('active', 'white')])

        style.configure("Secondary.TButton",
                        background=BACKGROUND_COLOR,
                        foreground=PRIMARY_COLOR,
                        font=FONT_BOLD,
                        padding=(15, 9),
                        borderwidth=1,
                        bordercolor=BORDER_COLOR)
        style.map("Secondary.TButton",
                  background=[('active', PRIMARY_LIGHT_COLOR)],
                  bordercolor=[('active', PRIMARY_COLOR)])

        style.configure("Success.TButton",
                        background=SUCCESS_COLOR,
                        foreground="white",
                        font=FONT_BOLD,
                        padding=(15, 9),
                        borderwidth=0)
        style.map("Success.TButton",
                  background=[('active', '#2E8A47')])

        style.configure("TProgressbar", thickness=5, background=PRIMARY_COLOR, troughcolor=PRIMARY_LIGHT_COLOR)

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.drop_zone = ttk.Frame(main_frame, style="TLabelframe", relief=tk.SOLID)
        self.drop_zone.pack(fill=tk.X, pady=(0, 20))
        self.drop_zone.pack_propagate(False)
        self.drop_zone.config(height=120)

        drop_label_large = ttk.Label(self.drop_zone, text="Drag & Drop Project Folder Here", font=FONT_LARGE_BOLD,
                                     foreground=TEXT_SECONDARY_COLOR)
        drop_label_large.pack(pady=(20, 5), expand=True)

        browse_frame = ttk.Frame(self.drop_zone)
        browse_frame.pack(pady=(0, 20), expand=True)
        ttk.Label(browse_frame, text="or", font=FONT_NORMAL, foreground=TEXT_SECONDARY_COLOR).pack(side=tk.LEFT,
                                                                                                   padx=10)
        browse_btn = ttk.Button(browse_frame, text="Browse Folder...", style="Secondary.TButton",
                                command=self._browse_folder)
        browse_btn.pack(side=tk.LEFT)

        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self._on_drop)
        self.drop_zone.bind("<Enter>", self._on_drop_enter)
        self.drop_zone.bind("<Leave>", self._on_drop_leave)
        for child in self.drop_zone.winfo_children():
            child.dnd_bind = self.drop_zone.dnd_bind
            child.drop_target_register = self.drop_zone.drop_target_register

        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=(0, 20))
        actions_frame.columnconfigure(0, weight=3)
        actions_frame.columnconfigure(1, weight=1)

        self.scan_btn = ttk.Button(actions_frame, text="Scan & Generate", style="Primary.TButton",
                                   command=self._scan_project, state=tk.DISABLED)
        self.scan_btn.grid(row=0, column=0, sticky="ew")

        self.edit_ignore_btn = ttk.Button(actions_frame, text="Edit .watchignore", style="Secondary.TButton",
                                          command=self._edit_watchignore, state=tk.DISABLED)
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
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=8, bg="#F8F9FA", fg=TEXT_COLOR, relief=tk.SOLID,
                                borderwidth=1, font=FONT_NORMAL)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.results_frame = ttk.LabelFrame(main_frame, text="Result", padding="10")

    def _on_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isdir(path):
            self._set_project_path(path)
            self._scan_project()
        else:
            messagebox.showerror("Error", f"Dropped item is not a valid directory: {path}")
        self._on_drop_leave(event)

    def _on_drop_enter(self, event):
        self.drop_zone.config(style="Primary.TLabelframe")

    def _on_drop_leave(self, event):
        self.drop_zone.config(style="TLabelframe")

    def _browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select Project Folder")
        if folder_path:
            self._set_project_path(folder_path)

    def _set_project_path(self, path):
        self.project_path = path
        self.path_var_display = os.path.basename(path)
        self.status_var.set(f"Project: {self.project_path}")
        self.scan_btn.config(state=tk.NORMAL)
        self.edit_ignore_btn.config(state=tk.NORMAL)
        self._log(f"Project selected: {path}")

    def _scan_project(self):
        if not self.project_path:
            messagebox.showerror("Error", "Please select a project folder first.")
            return

        self.scanner = FileScanner(self.project_path)
        self.combiner = FileCombiner(self.project_path)
        self.output_stats = {}

        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Starting scan...")
        self.results_frame.pack_forget()
        self.scan_btn.config(state=tk.DISABLED)

        self._log(f"Starting to scan project: {self.project_path}")

        thread = threading.Thread(target=self._process_project)
        thread.daemon = True
        thread.start()

    def _process_project(self):
        try:
            self._update_status("Scanning project files...", 0.1)
            text_files, ignored_items, all_files = self.scanner.scan(callback=self._scan_callback)
            self._log(f"Scan complete! Found {len(text_files)} text files.")

            self._update_status("Combining files...", 0.5)
            success, message, stats = self.combiner.combine(
                text_files, ignored_items,
                self.scanner.ignore_rules, all_files,
                callback=self._combine_callback
            )

            if success:
                self.output_stats = stats
                self._update_status(f"Success! Output file generated.", 1.0)
                self._log(f"Combined {stats['text_files']} files. Total characters: {stats['total_chars']:,}")
                self.root.after(0, self._show_results)
            else:
                self._update_status(f"Error: {message}", 1.0)
                self._log(f"Failed to combine files: {message}")
        except Exception as e:
            self._update_status(f"An unexpected error occurred: {str(e)}", 1.0)
            self._log(f"Exception occurred: {str(e)}")
        finally:
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))

    def _scan_callback(self, message, progress):
        self._update_status(message, progress * 0.5)

    def _combine_callback(self, message, progress):
        self._update_status(message, 0.5 + progress * 0.5)

    def _update_status(self, message, progress=None):
        def update():
            self.status_var.set(message)
            if progress is not None:
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

        info_frame = ttk.Frame(self.results_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text=f"Text Files: {stats['text_files']}", font=FONT_BOLD).pack(side=tk.LEFT,
                                                                                              padx=(0, 15))
        ttk.Label(info_frame, text=f"Ignored: {stats['ignored_items']}", font=FONT_BOLD).pack(side=tk.LEFT, padx=15)
        ttk.Label(info_frame, text=f"Total Chars: {stats['total_chars']:,}", font=FONT_BOLD).pack(side=tk.LEFT, padx=15)

        if stats['errors'] > 0:
            ttk.Label(info_frame, text=f"Errors: {stats['errors']}", font=FONT_BOLD, foreground="red").pack(
                side=tk.LEFT, padx=15)

        btn_frame = ttk.Frame(self.results_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.copy_btn = ttk.Button(btn_frame, text="Copy to Clipboard", style="Success.TButton",
                                   command=self._copy_to_clipboard)
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        open_file_btn = ttk.Button(btn_frame, text="Open Output File", style="Secondary.TButton",
                                   command=self._open_output_file)
        open_file_btn.pack(side=tk.LEFT, padx=5)

        open_dir_btn = ttk.Button(btn_frame, text="Open Output Directory", style="Secondary.TButton",
                                  command=self._open_output_dir)
        open_dir_btn.pack(side=tk.LEFT, padx=5)

        self.results_frame.pack(fill=tk.X, padx=0, pady=(15, 0))

    def _copy_to_clipboard(self):
        if self.combiner and os.path.exists(self.combiner.output_file):
            try:
                with open(self.combiner.output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self._log("Content copied to clipboard!")

                original_text = self.copy_btn.cget("text")
                self.copy_btn.config(text="Copied!", state=tk.DISABLED)
                self.root.after(2000, lambda: self.copy_btn.config(text=original_text, state=tk.NORMAL))
            except Exception as e:
                messagebox.showerror("Error", f"Could not copy to clipboard: {e}")
                self._log(f"Error copying to clipboard: {e}")
        else:
            messagebox.showerror("Error", "Output file not found. Please generate it first.")

    def _open_path(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Path not found: {path}")
            return
        try:
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', path])
            else:
                subprocess.call(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open path: {e}")

    def _open_output_file(self):
        if self.combiner and self.combiner.output_file:
            self._open_path(self.combiner.output_file)

    def _open_output_dir(self):
        if self.combiner and self.combiner.output_dir:
            self._open_path(self.combiner.output_dir)

    def _edit_watchignore(self):
        if not self.project_path:
            messagebox.showerror("Error", "Please select a project folder first")
            return

        if not self.scanner:
            self.scanner = FileScanner(self.project_path)

        watchignore_path = self.scanner.ignore_rules.get_watchignore_path()

        if not watchignore_path.exists():
            try:
                with open(watchignore_path, 'w', encoding='utf-8') as f:
                    f.write("# Add your custom ignore patterns here\n")
                    f.write("# Example: *.log\n")
                self._log(f"Created .watchignore at {watchignore_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create .watchignore: {e}")
                return

        self._open_path(watchignore_path)
