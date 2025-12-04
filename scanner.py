import os
import pathspec
from pathlib import Path
from ignore_rules import IgnoreRules
from file_utils import is_text_file, get_relative_path


class FileScanner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.ignore_rules = IgnoreRules(self.project_path)

    def scan(self, callback=None, cancel_event=None):
        # CẬP NHẬT LỚN: Thay đổi logic để tuân thủ thứ tự trong track_only.txt
        all_candidate_files = []
        all_files_for_tree = []  # Dùng để xây dựng cây thư mục đầy đủ

        # Bước 1: Quét một lần để lấy tất cả các file và thư mục ứng viên
        if callback: callback("Discovering all project files...", -1)
        for root, dirs, files in os.walk(self.project_path, topdown=True):
            if cancel_event and cancel_event.is_set(): break

            root_path = Path(root)
            rel_root = get_relative_path(root_path, self.project_path)
            if rel_root == '.': rel_root = ''

            # Bỏ qua các thư mục bị ignore ngay từ đầu để tăng tốc độ quét
            dirs[:] = [d for d in dirs if not self.ignore_rules.is_ignored(os.path.join(rel_root, d))]

            if rel_root:
                all_files_for_tree.append(rel_root)

            for d in dirs:
                all_files_for_tree.append(get_relative_path(root_path / d, self.project_path))

            for filename in files:
                file_path = root_path / filename
                rel_path = get_relative_path(file_path, self.project_path)
                all_files_for_tree.append(rel_path)
                all_candidate_files.append((file_path, rel_path))

        if callback: callback("Processing files based on your rules...", -1)

        # Bước 2: Xử lý file theo đúng thứ tự các quy tắc trong track_only.txt
        text_files = []
        ignored_items = []
        processed_paths = set()

        only_patterns = self.ignore_rules.settings.get("track_only", ["*"])
        use_ordered_scan = self.ignore_rules.has_user_defined_only_rules

        if use_ordered_scan:
            # Chạy scan theo thứ tự nếu người dùng đã tùy chỉnh track_only.txt
            for pattern in only_patterns:
                if cancel_event and cancel_event.is_set(): break
                spec = pathspec.PathSpec.from_lines('gitwildmatch', [pattern])

                for file_path, rel_path in all_candidate_files:
                    if rel_path in processed_paths:
                        continue

                    if spec.match_file(rel_path):
                        processed_paths.add(rel_path)
                        if self.ignore_rules.is_ignored(rel_path):
                            ignored_items.append((file_path, rel_path, "file"))
                            continue

                        if is_text_file(file_path):
                            text_files.append((file_path, rel_path))
                        else:
                            ignored_items.append((file_path, rel_path, "binary"))
        else:
            # Logic mặc định (quét theo alphabet) khi track_only là '*' cho hiệu quả
            for file_path, rel_path in all_candidate_files:
                if cancel_event and cancel_event.is_set(): break
                processed_paths.add(rel_path)

                if self.ignore_rules.is_ignored(rel_path):
                    ignored_items.append((file_path, rel_path, "file"))
                    continue

                if is_text_file(file_path):
                    text_files.append((file_path, rel_path))
                else:
                    ignored_items.append((file_path, rel_path, "binary"))

        # Bước 3: Đánh dấu các file còn lại là bị bỏ qua (vì không khớp rule trong track_only)
        if use_ordered_scan:
            for file_path, rel_path in all_candidate_files:
                if rel_path not in processed_paths:
                    ignored_items.append((file_path, rel_path, "file_rule(only)"))

        if cancel_event and cancel_event.is_set():
            if callback: callback("Scan cancelled by user.", -1)
            return [], [], []

        if callback:
            callback(f"Scan complete! Found {len(text_files)} text files and {len(ignored_items)} ignored items.", -1)

        return text_files, ignored_items, all_files_for_tree