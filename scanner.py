import os
from pathlib import Path
from ignore_rules import IgnoreRules
from file_utils import is_text_file, get_relative_path


class FileScanner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.ignore_rules = IgnoreRules(self.project_path)

    def scan(self, callback=None):
        """
        Scan the project directory recursively.
        Returns a tuple of (text_files, binary_files, ignored_items)
        If callback is provided, it's called with current progress information.
        """
        text_files = []
        binary_files = []
        ignored_items = []  # Will contain directories and individual files that are ignored
        ignored_dirs = set()  # Keep track of ignored directories to avoid including files inside them
        total_files_checked = 0

        # Walk through directory structure
        for root, dirs, files in os.walk(self.project_path):
            # Convert to Path objects
            root_path = Path(root)
            rel_root = get_relative_path(root_path, self.project_path)

            # Skip processing if parent directory is already ignored
            parent_ignored = False
            for ignored_dir in ignored_dirs:
                if rel_root.startswith(ignored_dir + os.sep) or rel_root == ignored_dir:
                    parent_ignored = True
                    break

            if parent_ignored:
                dirs[:] = []  # Clear dirs to skip processing subdirectories
                continue

            # Process directories - add ignored ones and skip their contents
            dirs_to_remove = []
            for d in dirs:
                dir_path = root_path / d
                rel_path = get_relative_path(dir_path, self.project_path)

                if self.ignore_rules.is_ignored(rel_path):
                    # Add directory to ignored items list
                    ignored_items.append((dir_path, rel_path, "directory"))
                    ignored_dirs.add(rel_path)
                    dirs_to_remove.append(d)

            # Remove ignored directories from dirs list
            for d in dirs_to_remove:
                dirs.remove(d)

            # Process files
            for filename in files:
                file_path = root_path / filename
                rel_path = get_relative_path(file_path, self.project_path)

                total_files_checked += 1
                if callback and total_files_checked % 10 == 0:
                    callback(f"Scanning: {rel_path}", total_files_checked)

                # Check if file should be ignored but not inside already ignored directory
                if self.ignore_rules.is_ignored(rel_path):
                    # Only add individual ignored files that aren't inside ignored directories
                    ignored_items.append((file_path, rel_path, "file"))
                    continue

                # Categorize as text or binary
                if is_text_file(file_path):
                    text_files.append((file_path, rel_path))
                else:
                    binary_files.append((file_path, rel_path))

        if callback:
            callback(
                f"Scan complete! Found {len(text_files)} text files, {len(binary_files)} binary files, and {len(ignored_items)} ignored items",
                total_files_checked)

        return text_files, binary_files, ignored_items
