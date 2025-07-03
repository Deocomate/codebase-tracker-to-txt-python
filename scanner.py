import os
from pathlib import Path
from ignore_rules import IgnoreRules
from file_utils import is_text_file, get_relative_path


class FileScanner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.ignore_rules = IgnoreRules(self.project_path)

    def scan(self, callback=None):
        text_files = []
        ignored_items = []
        all_files = []
        ignored_dirs = set()
        total_files_checked = 0

        for root, dirs, files in os.walk(self.project_path, topdown=True):
            root_path = Path(root)
            rel_root = get_relative_path(root_path, self.project_path)

            if rel_root == '.':
                rel_root = ''

            parent_ignored = any(
                rel_root == ignored_dir or rel_root.startswith(ignored_dir + os.sep)
                for ignored_dir in ignored_dirs
            )

            if parent_ignored:
                dirs[:] = []
                continue

            if rel_root:
                all_files.append(rel_root)

            dirs_to_remove = []
            for d in dirs:
                dir_path = root_path / d
                rel_path = get_relative_path(dir_path, self.project_path)
                all_files.append(rel_path)
                if self.ignore_rules.is_ignored(rel_path):
                    ignored_items.append((dir_path, rel_path, "directory"))
                    ignored_dirs.add(rel_path)
                    dirs_to_remove.append(d)

            for d in dirs_to_remove:
                dirs.remove(d)

            for filename in files:
                file_path = root_path / filename
                rel_path = get_relative_path(file_path, self.project_path)
                all_files.append(rel_path)
                total_files_checked += 1
                if callback and total_files_checked % 50 == 0:
                    callback(f"Scanning: {rel_path}", total_files_checked)

                if self.ignore_rules.is_ignored(rel_path):
                    ignored_items.append((file_path, rel_path, "file"))
                    continue

                if is_text_file(file_path):
                    text_files.append((file_path, rel_path))
                else:
                    ignored_items.append((file_path, rel_path, "binary"))

        if callback:
            callback(
                f"Scan complete! Found {len(text_files)} text files and {len(ignored_items)} ignored items.",
                total_files_checked)

        return text_files, ignored_items, all_files
