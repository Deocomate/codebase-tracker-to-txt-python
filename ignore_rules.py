import os
import pathspec
from pathlib import Path
from file_utils import ensure_directory

DEFAULT_IGNORE_PATTERNS = [
    '.git/', 'node_modules/', 'vendor/', 'bower_components/', 'storage/',
    'build/', 'dist/', 'out/', 'target/', '.svn/', '.hg/', '.bzr/', '.idea/',
    '.vscode/', '.project/', '.settings/', '__pycache__/', '.pytest_cache/',
    '.mypy_cache/', '.ruff_cache/', 'coverage/', 'logs/', 'tmp/', 'temp/',
    '*.lockb', '*.log', '*.tmp', '*.bak', '*.swp', '*.DS_Store'
]

# MỚI: Hằng số cho file track_only.txt
TRACK_ONLY_FILENAME = "track_only.txt"
TRACK_ONLY_HEADER = "# File này giúp bạn CHỈ ĐỊNH các file và thư mục cần quét (Cú pháp tương tự .gitignore)."
TRACK_ONLY_EXAMPLE = "# Mặc định là '*' (quét tất cả).\n# Ví dụ: chỉ quét thư mục 'src' và các file '.py':\n# src/\n# *.py\n"
DEFAULT_TRACK_ONLY_PATTERN = "*"

# Cập nhật hằng số cho track_ignore.txt để rõ ràng hơn
TRACK_IGNORE_FILENAME = "track_ignore.txt"
TRACK_IGNORE_HEADER = "# File này giúp bạn BỎ QUA (ignore) các file và thư mục khỏi quá trình quét (Cú pháp tương tự .gitignore)."
TRACK_IGNORE_EXAMPLE = "# Ví dụ: build/\n# Ví dụ: *.log\n"


class IgnoreRules:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.codebase_dir = self.project_path / '.codebase'

        # Ignore rules (deny list)
        self.ignore_rules = []
        self.gitignore_found = False
        self.track_ignore_found = False
        self.gitignore_patterns = []
        self.track_ignore_patterns = []
        self.default_patterns = DEFAULT_IGNORE_PATTERNS.copy()

        # MỚI: Only rules (allow list)
        self.track_only_spec = None
        self.track_only_found = False
        self.track_only_patterns = []
        self.has_user_defined_only_rules = False

        ensure_directory(self.codebase_dir)

        self._load_gitignore()
        self._load_track_ignore()
        self._add_default_patterns()

        # MỚI: Tải quy tắc track_only
        self._load_track_only()

    def _load_gitignore(self):
        """Load rules from .gitignore file if it exists"""
        gitignore_path = self.project_path / '.gitignore'
        if gitignore_path.exists() and gitignore_path.is_file():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_content = f.read()
                gitignore_lines = gitignore_content.splitlines()
                self.gitignore_patterns = [line for line in gitignore_lines if
                                           line.strip() and not line.strip().startswith('#')]
                self.ignore_rules.append(pathspec.PathSpec.from_lines('gitwildmatch', gitignore_lines))
                self.gitignore_found = True
            except Exception as e:
                print(f"Error loading .gitignore: {e}")

    def _load_track_ignore(self):
        """Load rules from track_ignore.txt. If it doesn't exist, create it."""
        track_ignore_path = self.get_track_ignore_path()
        try:
            if not track_ignore_path.exists():
                with open(track_ignore_path, 'w', encoding='utf-8') as f:
                    f.write(TRACK_IGNORE_HEADER + '\n\n')
                    f.write(TRACK_IGNORE_EXAMPLE)
                self.track_ignore_found = True
                return

            with open(track_ignore_path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()

            self.track_ignore_patterns = [line.strip() for line in lines if
                                          line.strip() and not line.strip().startswith('#')]
            if self.track_ignore_patterns:
                self.ignore_rules.append(pathspec.PathSpec.from_lines('gitwildmatch', self.track_ignore_patterns))
            self.track_ignore_found = True
        except Exception as e:
            print(f"Error loading or creating {TRACK_IGNORE_FILENAME}: {e}")

    # MỚI: Hàm để tải và xử lý track_only.txt
    def _load_track_only(self):
        """Load rules from track_only.txt. If it doesn't exist, create it with '*'."""
        track_only_path = self.get_track_only_path()
        try:
            if not track_only_path.exists():
                with open(track_only_path, 'w', encoding='utf-8') as f:
                    f.write(TRACK_ONLY_HEADER + '\n\n')
                    f.write(TRACK_ONLY_EXAMPLE)
                    f.write(f"{DEFAULT_TRACK_ONLY_PATTERN}\n")
                self.track_only_found = True

            with open(track_only_path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()

            self.track_only_patterns = [line.strip() for line in lines if
                                        line.strip() and not line.strip().startswith('#')]

            # Nếu file rỗng hoặc chỉ chứa '*', coi như không có quy tắc tùy chỉnh
            if not self.track_only_patterns or self.track_only_patterns == [DEFAULT_TRACK_ONLY_PATTERN]:
                self.has_user_defined_only_rules = False
                # Vẫn tạo spec để match tất cả mọi thứ
                self.track_only_spec = pathspec.PathSpec.from_lines('gitwildmatch', [DEFAULT_TRACK_ONLY_PATTERN])
            else:
                self.has_user_defined_only_rules = True
                self.track_only_spec = pathspec.PathSpec.from_lines('gitwildmatch', self.track_only_patterns)

            self.track_only_found = True
        except Exception as e:
            print(f"Error loading or creating {TRACK_ONLY_FILENAME}: {e}")

    def _add_default_patterns(self):
        """Add default ignore patterns"""
        self.ignore_rules.append(pathspec.PathSpec.from_lines('gitwildmatch', DEFAULT_IGNORE_PATTERNS))

    def _normalize_path(self, path):
        if isinstance(path, Path):
            rel_path = path.relative_to(self.project_path) if path.is_absolute() else path
            return str(rel_path).replace('\\', '/')
        return path.replace('\\', '/')

    # MỚI: Kiểm tra xem một đường dẫn có được phép bởi track_only không
    def is_tracked_by_only_rules(self, path):
        """Check if a path is allowed by track_only.txt rules."""
        if not self.has_user_defined_only_rules:
            return True  # Nếu chỉ có '*', cho phép tất cả
        path_str = self._normalize_path(path)
        return self.track_only_spec.match_file(path_str)

    def is_ignored(self, path):
        """Check if a path should be ignored by any ignore rule."""
        path_str = self._normalize_path(path)

        if path_str == '.codebase' or path_str.startswith('.codebase/'):
            return True

        for rule_set in self.ignore_rules:
            if rule_set.match_file(path_str):
                return True

        return False

    def get_rule_summary(self):
        """Get a summary of all rules for reporting"""
        # CẬP NHẬT: Thêm 'track_only' vào summary
        rules_info = {
            'gitignore': {
                'found': self.gitignore_found,
                'patterns': self.gitignore_patterns
            },
            'track_ignore': {
                'found': self.track_ignore_found,
                'patterns': self.track_ignore_patterns
            },
            'track_only': {
                'found': self.track_only_found,
                'patterns': self.track_only_patterns
            },
            'default': {
                'patterns': self.default_patterns
            }
        }
        return rules_info

    def get_track_ignore_path(self):
        """Return the path to the track_ignore.txt file"""
        return self.codebase_dir / TRACK_IGNORE_FILENAME

    # MỚI: Lấy đường dẫn tới file track_only.txt
    def get_track_only_path(self):
        """Return the path to the track_only.txt file"""
        return self.codebase_dir / TRACK_ONLY_FILENAME
