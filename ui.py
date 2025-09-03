import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os
import platform
import subprocess
import struct
from pathlib import Path
from tkinterdnd2 import DND_FILES
import shutil

if platform.system() == "Windows":
    try:
        import win32clipboard
        import win32con

        WINDOWS_COPY_SUPPORT = True
    except ImportError:
        WINDOWS_COPY_SUPPORT = False
else:
    WINDOWS_COPY_SUPPORT = False

from processor import ProjectProcessor
from scanner import FileScanner

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
FONT_NORMAL = (FONT_FAMILY, 9)
FONT_BOLD = (FONT_FAMILY, 10, "bold")


class CodebaseTrackerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Codebase Tracker")

        initial_width = 720
        initial_height = 520
        self.root.geometry(f"{initial_width}x{initial_height}")

        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        margin = 60
        x = screen_width - initial_width - margin
        y = (screen_height - initial_height) // 2
        self.root.geometry(f'{initial_width}x{initial_height}+{x}+{y}')

        self.root.minsize(680, 500)
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
        style.configure("TEntry", fieldbackground="white", bordercolor=BORDER_COLOR, lightcolor=BORDER_COLOR,
                        darkcolor=BORDER_COLOR)
        style.map("TEntry", bordercolor=[('focus', PRIMARY_COLOR)])
        style.configure("TLabelframe", background=BACKGROUND_COLOR, bordercolor=SOFT_BORDER_COLOR, relief=tk.SOLID,
                        borderwidth=1)
        style.configure("TLabelframe.Label", background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=FONT_BOLD)

        style.configure("Primary.TButton", background=PRIMARY_COLOR, foreground="white", font=FONT_BOLD,
                        padding=(15, 10), borderwidth=0)
        style.map("Primary.TButton", background=[('active', BUTTON_HOVER_COLOR), ('disabled', '#A0C3FF')])

        style.configure("Secondary.TButton", background=BACKGROUND_COLOR, foreground=PRIMARY_COLOR, font=FONT_BOLD,
                        padding=(10, 7), borderwidth=1, bordercolor=BORDER_COLOR)
        style.map("Secondary.TButton", background=[('active', PRIMARY_LIGHT_COLOR)],
                  bordercolor=[('active', PRIMARY_COLOR)])

        style.configure("Small.Secondary.TButton", background=BACKGROUND_COLOR, foreground=PRIMARY_COLOR,
                        font=FONT_NORMAL, padding=(8, 4), borderwidth=1, bordercolor=BORDER_COLOR)
        style.map("Small.Secondary.TButton", background=[('active', PRIMARY_LIGHT_COLOR)],
                  bordercolor=[('active', PRIMARY_COLOR)])

        style.configure("Success.TButton", background=SUCCESS_COLOR, foreground="white", font=FONT_BOLD,
                        padding=(12, 8), borderwidth=0)
        style.map("Success.TButton", background=[('active', '#2E8A47')])

        style.configure("Cancel.TButton", background=CANCEL_COLOR, foreground="white", font=FONT_BOLD, padding=(15, 10),
                        borderwidth=0)
        style.map("Cancel.TButton", background=[('active', CANCEL_HOVER_COLOR)])

        style.configure("TProgressbar", thickness=4, background=PRIMARY_COLOR, troughcolor=PRIMARY_LIGHT_COLOR)

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        path_input_frame = ttk.LabelFrame(main_frame, text="Project Path", padding="10")
        path_input_frame.pack(fill=tk.X, pady=(0, 10))
        path_input_frame.columnconfigure(0, weight=1)

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_input_frame, textvariable=self.path_var, font=FONT_NORMAL)
        self.path_entry.grid(row=0, column=0, sticky="ew", ipady=4)

        self.path_var.trace_add("write", self._validate_path_from_entry)

        path_buttons_frame = ttk.Frame(path_input_frame)
        path_buttons_frame.grid(row=0, column=1, sticky="e", padx=(8, 0))

        paste_btn = ttk.Button(path_buttons_frame, text="Paste", style="Small.Secondary.TButton",
                               command=self._paste_path)
        paste_btn.pack(side=tk.LEFT, padx=(0, 5))
        browse_btn = ttk.Button(path_buttons_frame, text="Browse...", style="Small.Secondary.TButton",
                                command=self._browse_folder)
        browse_btn.pack(side=tk.LEFT)

        path_input_frame.drop_target_register(DND_FILES)
        path_input_frame.dnd_bind('<<Drop>>', self._on_drop)
        self.path_entry.drop_target_register(DND_FILES)
        self.path_entry.dnd_bind('<<Drop>>', self._on_drop)

        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        # CẬP NHẬT: Chia cột cho 3 nút
        actions_frame.columnconfigure(0, weight=2)
        actions_frame.columnconfigure(1, weight=1)
        actions_frame.columnconfigure(2, weight=1)

        self.scan_btn = ttk.Button(actions_frame, text="Scan & Generate", style="Primary.TButton",
                                   command=self._scan_project, state=tk.DISABLED)
        self.scan_btn.grid(row=0, column=0, sticky="ew")

        self.cancel_btn = ttk.Button(actions_frame, text="Cancel", style="Cancel.TButton", command=self._on_cancel)

        # MỚI: Thêm nút Edit track_only.txt
        self.edit_only_btn = ttk.Button(actions_frame, text="Edit track_only.txt", style="Secondary.TButton",
                                        command=self._edit_track_only, state=tk.DISABLED)
        self.edit_only_btn.grid(row=0, column=1, sticky="ew", padx=(10, 5))

        self.edit_ignore_btn = ttk.Button(actions_frame, text="Edit track_ignore.txt", style="Secondary.TButton",
                                          command=self._edit_track_ignore, state=tk.DISABLED)
        self.edit_ignore_btn.grid(row=0, column=2, sticky="ew")

        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_var = tk.StringVar(value="Select or paste a project folder to begin.")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, wraplength=650)
        status_label.pack(fill=tk.X, pady=(0, 5))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=1.0)
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.results_frame = ttk.LabelFrame(main_frame, text="Result", padding="10")

    def _on_drop(self, event):
        path = event.data.strip('{}')
        self.path_var.set(path)

    def _browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select Project Folder")
        if folder_path:
            self.path_var.set(folder_path)

    def _paste_path(self):
        try:
            clipboard_content = self.root.clipboard_get()
            self.path_var.set(clipboard_content)
        except tk.TclError:
            self.status_var.set("Clipboard is empty or does not contain text.")

    def _add_to_gitignore(self, project_path):
        gitignore_path = os.path.join(project_path, '.gitignore')
        line_to_add = ".codebase/"
        try:
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    if line_to_add not in content:
                        f.seek(0, os.SEEK_END)
                        if not content.endswith('\n'):
                            f.write('\n')
                        f.write(f'\n# Added by CodebaseTracker\n{line_to_add}\n')
        except Exception as e:
            self.status_var.set(f"Could not update .gitignore: {e}")

    def _validate_path_from_entry(self, *args):
        path = self.path_var.get()
        if os.path.isdir(path):
            self.project_path = path
            self.status_var.set(f"Project path is valid. Ready to scan.")
            self.scan_btn.config(state=tk.NORMAL)
            self.edit_ignore_btn.config(state=tk.NORMAL)
            self.edit_only_btn.config(state=tk.NORMAL)  # MỚI: Bật nút
            self._add_to_gitignore(path)
        else:
            self.project_path = None
            if path:
                self.status_var.set("Invalid path. Please provide a valid project folder.")
            self.scan_btn.config(state=tk.DISABLED)
            self.edit_ignore_btn.config(state=tk.DISABLED)
            self.edit_only_btn.config(state=tk.DISABLED)  # MỚI: Tắt nút

    def _on_cancel(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self.status_var.set("Cancellation requested...")
            self.cancel_event.set()
            self.cancel_btn.config(state=tk.DISABLED, text="Cancelling...")

    def _scan_project(self):
        if not self.project_path:
            messagebox.showerror("Error", "Please select a valid project folder first.")
            return

        self.processor = ProjectProcessor(self.project_path)
        self.output_stats = {}
        self.cancel_event.clear()
        self.progress_var.set(0)
        self.status_var.set("Starting scan...")
        self.results_frame.pack_forget()
        self.scan_btn.grid_remove()
        self.cancel_btn.grid(row=0, column=0, sticky="ew")
        self.cancel_btn.config(state=tk.NORMAL, text="Cancel")
        self.edit_ignore_btn.config(state=tk.DISABLED)
        self.edit_only_btn.config(state=tk.DISABLED)  # MỚI: Tắt nút khi đang chạy
        self.path_entry.config(state=tk.DISABLED)

        self.worker_thread = threading.Thread(target=self._process_project)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def _process_project(self):
        if not self.processor:
            self.root.after(0, self._restore_ui_state)
            return

        try:
            success, message, stats = self.processor.run(
                self._scan_callback, self._combine_callback, self.cancel_event
            )

            if self.cancel_event.is_set():
                self._update_status("Process cancelled.", 0)
                return

            if success:
                self.output_stats = stats
                self._update_status("Success! Output file generated.", 1.0)
                self.root.after(0, self._show_results)
            else:
                self._update_status(f"Error: {message}", 1.0)
                messagebox.showerror("Error", f"An error occurred: {message}")
        finally:
            self.root.after(0, self._restore_ui_state)

    def _restore_ui_state(self):
        self.cancel_btn.grid_remove()
        self.scan_btn.grid(row=0, column=0, sticky="ew")
        self.path_entry.config(state=tk.NORMAL)
        self._validate_path_from_entry()

    def _scan_callback(self, message, progress):
        self._update_status(message, -1)

    def _combine_callback(self, message, progress):
        self._update_status(message, progress)

    def _update_status(self, message, progress=None):
        def update():
            self.status_var.set(message)
            if progress is not None and progress >= 0:
                self.progress_var.set(progress)

        self.root.after(0, update)

    def _show_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        stats = self.output_stats
        if not stats: return

        info_frame = ttk.Frame(self.results_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        stats_text = f"Text Files: {stats.get('text_files', 0)}   | Ignored: {stats.get('ignored_items', 0)}   |   Chars: {stats.get('total_chars', 0):,}"
        ttk.Label(info_frame, text=stats_text, font=FONT_BOLD).pack(side=tk.LEFT)
        if stats.get('errors', 0) > 0:
            ttk.Label(info_frame, text=f"   Errors: {stats['errors']}", font=FONT_BOLD, foreground="red").pack(
                side=tk.LEFT)

        output_path_frame = ttk.Frame(self.results_frame)
        output_path_frame.pack(fill=tk.X, pady=(5, 10))
        output_path_frame.columnconfigure(0, weight=1)

        self.output_path_var = tk.StringVar(value=stats.get('output_file', ''))
        path_display_entry = ttk.Entry(output_path_frame, textvariable=self.output_path_var, state="readonly",
                                       font=FONT_NORMAL)
        path_display_entry.grid(row=0, column=0, sticky="ew")

        copy_path_btn = ttk.Button(output_path_frame, text="Copy Path", style="Small.Secondary.TButton",
                                   command=self._copy_output_path)
        copy_path_btn.grid(row=0, column=1, sticky="e", padx=(8, 0))

        btn_frame = ttk.Frame(self.results_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        if WINDOWS_COPY_SUPPORT:
            self.copy_file_btn = ttk.Button(btn_frame, text="Copy File", style="Success.TButton",
                                            command=self._copy_file_to_clipboard)
            self.copy_file_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        open_file_btn = ttk.Button(btn_frame, text="Open File", style="Secondary.TButton",
                                   command=self._open_output_file)
        open_file_btn.pack(side=tk.LEFT, padx=(0, 5))

        open_dir_btn = ttk.Button(btn_frame, text="Open Dir", style="Secondary.TButton", command=self._open_output_dir)
        open_dir_btn.pack(side=tk.LEFT, padx=(0, 5))

        clear_btn = ttk.Button(btn_frame, text="Clear Output", style="Secondary.TButton", command=self._clear_output)
        clear_btn.pack(side=tk.LEFT)

        self.results_frame.pack(fill=tk.BOTH, pady=(10, 0), expand=True)

    def _clear_output(self):
        if not self.project_path:
            return

        output_dir_path = os.path.join(self.project_path, '.codebase')
        if not os.path.isdir(output_dir_path):
            self.status_var.set("Output directory (.codebase) not found.")
            return

        try:
            shutil.rmtree(output_dir_path)
            self.status_var.set("Output directory '.codebase' has been deleted.")
            self.results_frame.pack_forget()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete directory: {e}")

    def _copy_file_to_clipboard(self):
        if not WINDOWS_COPY_SUPPORT:
            messagebox.showinfo("Info", "This feature is only available on Windows.")
            return
        output_file = self.output_stats.get('output_file')
        if not output_file or not os.path.exists(output_file):
            messagebox.showerror("Error", "Output file not found.")
            return
        try:
            file_path = os.path.abspath(output_file)
            file_list_bytes = (file_path + '\0\0').encode('utf-16le')
            dropfiles_struct = struct.pack('IIIII', 20, 0, 0, 0, 1)
            data = dropfiles_struct + file_list_bytes
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_HDROP, data)
                self.status_var.set("File copied to clipboard. You can now paste it in Explorer.")

                original_text = self.copy_file_btn.cget("text")
                self.copy_file_btn.config(text="Copied!", state=tk.DISABLED)
                self.root.after(2000, lambda: self.copy_file_btn.config(text=original_text, state=tk.NORMAL))
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy file to clipboard: {e}")

    def _copy_output_path(self):
        path = self.output_path_var.get()
        if path:
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            self.status_var.set("Output file path copied to clipboard!")

    def _open_path(self, path):
        try:
            if not os.path.exists(path):
                messagebox.showerror("Error", f"Path not found: {path}")
                return
            if platform.system() == 'Windows':
                os.startfile(os.path.normpath(path))
            elif platform.system() == 'Darwin':
                subprocess.run(['open', path], check=True)
            else:
                subprocess.run(['xdg-open', path], check=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open path: {e}")

    def _open_output_file(self):
        output_file = self.output_stats.get('output_file')
        if output_file:
            self._open_path(output_file)

    def _open_output_dir(self):
        output_dir = self.output_stats.get('output_file')
        if output_dir:
            self._open_path(os.path.dirname(output_dir))

    def _edit_track_ignore(self):
        if not self.project_path:
            messagebox.showerror("Error", "Please select a project folder first")
            return
        scanner = FileScanner(self.project_path)
        track_ignore_path = scanner.ignore_rules.get_track_ignore_path()
        self._open_path(track_ignore_path)

    # MỚI: Hàm để mở file track_only.txt
    def _edit_track_only(self):
        if not self.project_path:
            messagebox.showerror("Error", "Please select a project folder first")
            return
        # Tạo scanner tạm để lấy đường dẫn file một cách an toàn
        scanner = FileScanner(self.project_path)
        track_only_path = scanner.ignore_rules.get_track_only_path()
        self._open_path(track_only_path)