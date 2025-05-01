import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os
from pathlib import Path

# Import tkinterdnd2 for drag & drop support
from tkinterdnd2 import DND_FILES, TkinterDnD

from scanner import FileScanner
from combiner import FileCombiner
from file_utils import format_file_size


class CodebaseTrackerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Codebase Tracker")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.project_path = None
        self.scanner = None
        self.combiner = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Project selection frame
        project_frame = ttk.LabelFrame(main_frame, text="Project Selection", padding="10")
        project_frame.pack(fill=tk.X, padx=5, pady=5)

        # Project path entry and browse button
        path_frame = ttk.Frame(project_frame)
        path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(path_frame, text="Project Path:").pack(side=tk.LEFT)

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Enable drag and drop for the entry
        self.path_entry.drop_target_register(DND_FILES)
        self.path_entry.dnd_bind('<<Drop>>', self._on_drop)

        browse_btn = ttk.Button(path_frame, text="Browse", command=self._browse_folder)
        browse_btn.pack(side=tk.LEFT)

        # Actions frame
        actions_frame = ttk.Frame(project_frame)
        actions_frame.pack(fill=tk.X, pady=5)

        # Scan button
        scan_btn = ttk.Button(actions_frame, text="Scan & Generate", command=self._scan_project)
        scan_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Edit watchignore button
        edit_ignore_btn = ttk.Button(actions_frame, text="Edit .watchignore", command=self._edit_watchignore)
        edit_ignore_btn.pack(side=tk.RIGHT)

        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=1.0)
        self.progress_bar.pack(fill=tk.X, pady=5)

        # Status message
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, wraplength=700)
        status_label.pack(fill=tk.X, pady=5)

        # Log text area with scrollbar
        log_frame = ttk.Frame(status_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Results frame
        self.results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        self.results_frame.pack(fill=tk.X, padx=5, pady=5)

        # Open output button (initially hidden)
        self.open_btn = ttk.Button(self.results_frame, text="Open Output File", command=self._open_output_file)
        self.open_output_dir_btn = ttk.Button(self.results_frame, text="Open Output Directory",
                                              command=self._open_output_dir)

        # Hide results frame initially
        self.results_frame.pack_forget()

    def _on_drop(self, event):
        """Handle drag and drop events"""
        # Parse the data from the drop event
        data = event.data

        # Clean up the path (remove {} or "" on Windows)
        if data.startswith('{') and data.endswith('}'):
            data = data[1:-1]
        if data.startswith('"') and data.endswith('"'):
            data = data[1:-1]

        # If there are multiple paths, take only the first one
        paths = data.split()
        if not paths:
            return

        path = paths[0]

        # Check if the path exists and is a directory
        if os.path.isdir(path):
            self.path_var.set(path)
            # Auto-scan when dropping a folder
            self._scan_project()
        else:
            messagebox.showerror("Error", f"Dropped item is not a valid directory: {path}")

    def _browse_folder(self):
        """Open dialog to select project folder"""
        folder_path = filedialog.askdirectory(title="Select Project Folder")
        if folder_path:
            self.path_var.set(folder_path)

    def _scan_project(self):
        """Start scanning the project in a separate thread"""
        project_path = self.path_var.get().strip()

        if not project_path:
            messagebox.showerror("Error", "Please select a project folder")
            return

        if not os.path.isdir(project_path):
            messagebox.showerror("Error", "Selected path is not a valid directory")
            return

        self.project_path = project_path
        self.scanner = FileScanner(project_path)
        self.combiner = FileCombiner(project_path)

        # Reset UI
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Starting scan...")
        self.results_frame.pack_forget()

        # Log start
        self._log(f"Starting to scan project: {project_path}")

        # Start processing in a separate thread
        thread = threading.Thread(target=self._process_project)
        thread.daemon = True
        thread.start()

    def _process_project(self):
        """Process the project (scan and combine) in a background thread"""
        try:
            # Scan files
            self._update_status("Scanning project files...", 0.1)
            text_files, binary_files, ignored_files = self.scanner.scan(callback=self._scan_callback)

            self._log(f"Scan complete!")
            self._log(f"Found {len(text_files)} text files and {len(binary_files)} binary files")
            self._log(f"Ignored {len(ignored_files)} items based on ignore rules")

            # Combine files
            self._update_status("Combining files...", 0.5)
            success, message, stats = self.combiner.combine(
                text_files,
                binary_files,
                ignored_files,
                self.scanner.ignore_rules,
                callback=self._combine_callback
            )

            if success:
                self._update_status(f"Success! {message}", 1.0)
                self._log(f"Combined {stats['text_files']} text files into {stats['output_file']}")
                self._log(f"Total characters in output: {stats['total_chars']:,}")

                # Show results frame
                self.root.after(0, self._show_results, stats)
            else:
                self._update_status(f"Error: {message}", 1.0)
                self._log(f"Failed to combine files: {message}")

        except Exception as e:
            self._update_status(f"Error: {str(e)}", 1.0)
            self._log(f"Exception occurred: {str(e)}")

    def _scan_callback(self, message, progress):
        """Callback for scanner progress updates"""
        self._update_status(message, progress * 0.5)  # Scanning is 50% of total progress

    def _combine_callback(self, message, progress):
        """Callback for combiner progress updates"""
        self._update_status(message, 0.5 + progress * 0.5)  # Combining is the second 50% of progress

    def _update_status(self, message, progress=None):
        """Update status message and progress bar"""

        def update():
            self.status_var.set(message)
            if progress is not None:
                self.progress_var.set(progress)
            self._log(message)

        self.root.after(0, update)

    def _log(self, message):
        """Add message to log with timestamp"""
        import time
        timestamp = time.strftime("%H:%M:%S")

        def update():
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)

        self.root.after(0, update)

    def _show_results(self, stats):
        """Show results frame with statistics"""
        # Clear existing widgets
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Create stats labels
        ttk.Label(self.results_frame,
                  text=f"Generated file: {Path(stats['output_file']).name}").pack(anchor=tk.W)

        ttk.Label(self.results_frame,
                  text=f"Files processed: {stats['text_files']} text, {stats['binary_files']} binary").pack(anchor=tk.W)

        ttk.Label(self.results_frame,
                  text=f"Ignored items: {stats['ignored_files']}").pack(anchor=tk.W)

        ttk.Label(self.results_frame,
                  text=f"Total characters: {stats['total_chars']:,}").pack(anchor=tk.W)

        if stats['errors'] > 0:
            ttk.Label(self.results_frame,
                      text=f"Errors encountered: {stats['errors']}",
                      foreground="red").pack(anchor=tk.W)

        # Button frame
        btn_frame = ttk.Frame(self.results_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.open_btn = ttk.Button(btn_frame, text="Open Output File", command=self._open_output_file)
        self.open_btn.pack(side=tk.LEFT, padx=5)

        self.open_output_dir_btn = ttk.Button(btn_frame, text="Open Output Directory", command=self._open_output_dir)
        self.open_output_dir_btn.pack(side=tk.LEFT, padx=5)

        # Show the frame
        self.results_frame.pack(fill=tk.X, padx=5, pady=5)

    def _open_output_file(self):
        """Open the generated output file"""
        if self.combiner and os.path.exists(self.combiner.output_file):
            import platform
            import subprocess

            path = self.combiner.output_file

            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', path])
            else:  # Linux
                subprocess.call(['xdg-open', path])
        else:
            messagebox.showerror("Error", "Output file not found")

    def _open_output_dir(self):
        """Open the output directory"""
        if self.combiner and os.path.exists(self.combiner.output_dir):
            import platform
            import subprocess

            path = self.combiner.output_dir

            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', path])
            else:  # Linux
                subprocess.call(['xdg-open', path])
        else:
            messagebox.showerror("Error", "Output directory not found")

    def _edit_watchignore(self):
        """Open the .watchignore file for editing"""
        if not self.project_path:
            messagebox.showerror("Error", "Please select a project folder first")
            return

        # Initialize scanner if needed
        if not self.scanner:
            self.scanner = FileScanner(self.project_path)

        # Get path to .watchignore
        watchignore_path = self.scanner.ignore_rules.get_watchignore_path()

        # Make sure file exists
        if not watchignore_path.exists():
            try:
                with open(watchignore_path, 'w', encoding='utf-8') as f:
                    f.write("# Add your custom ignore patterns here\n")
                    f.write("# Example: *.log\n")
                    f.write("# Example: temp/\n")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create .watchignore: {e}")
                return

        # Open the file
        import platform
        import subprocess

        try:
            if platform.system() == 'Windows':
                os.startfile(watchignore_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', watchignore_path])
            else:  # Linux
                subprocess.call(['xdg-open', watchignore_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open .watchignore: {e}")
