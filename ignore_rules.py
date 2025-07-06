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

# --- NEW: Constants for the custom ignore file ---
TRACK_IGNORE_FILENAME = "track_ignore.txt"
TRACK_IGNORE_HEADER = "# File này giúp bạn bỏ qua (ignore) các file và thư mục không cần thiết khỏi quá trình quét codebase của bạn (Cú pháp tương tự như .gitignore). Bạn có thể bỏ qua code của thư viện, file nhị phân, folder không cần thiết để codebase nhẹ hơn."
TRACK_IGNORE_EXAMPLE = "# Ví dụ: build/\n# Ví dụ: *.log\n"


class IgnoreRules:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.codebase_dir = self.project_path / '.codebase'
        self.rules = []
        self.gitignore_found = False
        
        # --- UPDATED: Renamed variables for clarity ---
        self.track_ignore_found = False
        self.gitignore_patterns = []
        self.track_ignore_patterns = []
        self.default_patterns = DEFAULT_IGNORE_PATTERNS.copy()

        ensure_directory(self.codebase_dir)

        self._load_gitignore()
        # --- UPDATED: Call the new method ---
        self._load_track_ignore()
        self._add_default_patterns()

    def _load_gitignore(self):
        """Load rules from .gitignore file if it exists"""
        gitignore_path = self.project_path / '.gitignore'
        if gitignore_path.exists() and gitignore_path.is_file():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_content = f.read()
                gitignore_lines = gitignore_content.splitlines()
                self.gitignore_patterns = [line for line in gitignore_lines if line.strip() and not line.strip().startswith('#')]
                self.rules.append(pathspec.PathSpec.from_lines('gitwildmatch', gitignore_lines))
                self.gitignore_found = True
            except Exception as e:
                print(f"Error loading .gitignore: {e}")

    def _load_track_ignore(self):
        """
        Load rules from track_ignore.txt.
        If it doesn't exist, create it with a helpful header.
        If it exists, ensure the header is present.
        """
        track_ignore_path = self.get_track_ignore_path()
        
        try:
            if track_ignore_path.exists() and track_ignore_path.is_file():
                with open(track_ignore_path, 'r+', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Ensure header exists
                    if not lines or lines[0].strip() != TRACK_IGNORE_HEADER:
                        content = f.read()
                        f.seek(0, 0)
                        f.write(TRACK_IGNORE_HEADER + '\n\n' + content)
                        lines.insert(0, TRACK_IGNORE_HEADER + '\n')

                # Filter out header and comments to get actual patterns
                user_patterns = [
                    line.strip() for line in lines 
                    if line.strip() and not line.strip().startswith('#')
                ]
                if user_patterns:
                    self.track_ignore_patterns = user_patterns
                    self.rules.append(pathspec.PathSpec.from_lines('gitwildmatch', self.track_ignore_patterns))
                self.track_ignore_found = True
            else:
                # Create the file with header and examples
                with open(track_ignore_path, 'w', encoding='utf-8') as f:
                    f.write(TRACK_IGNORE_HEADER + '\n\n')
                    f.write(TRACK_IGNORE_EXAMPLE)
                self.track_ignore_patterns = [] # No user patterns yet
                self.track_ignore_found = True # File is now "found"
        except Exception as e:
            print(f"Error loading or creating {TRACK_IGNORE_FILENAME}: {e}")


    def _add_default_patterns(self):
        """Add default ignore patterns"""
        self.rules.append(pathspec.PathSpec.from_lines('gitwildmatch', DEFAULT_IGNORE_PATTERNS))

    def is_ignored(self, path):
        """
        Check if a path should be ignored based on rules.
        Returns True if the path should be ignored.
        """
        if isinstance(path, Path):
            rel_path = path.relative_to(self.project_path) if path.is_absolute() else path
            path_str = str(rel_path).replace('\\', '/')
        else:
            path_str = path.replace('\\', '/')

        if path_str == '.codebase' or path_str.startswith('.codebase/'):
            return True

        for rule_set in self.rules:
            if rule_set.match_file(path_str):
                return True

        return False

    def get_rule_summary(self):
        """Get a summary of all ignore rules for reporting"""
        # --- UPDATED: Use the new key 'track_ignore' ---
        rules_info = {
            'gitignore': {
                'found': self.gitignore_found,
                'patterns': self.gitignore_patterns
            },
            'track_ignore': {
                'found': self.track_ignore_found,
                'patterns': self.track_ignore_patterns
            },
            'default': {
                'patterns': self.default_patterns
            }
        }
        return rules_info

    def get_track_ignore_path(self):
        """Return the path to the track_ignore.txt file"""
        # --- UPDATED: Use the new filename constant ---
        return self.codebase_dir / TRACK_IGNORE_FILENAME
