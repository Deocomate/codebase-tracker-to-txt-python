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


class IgnoreRules:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.codebase_dir = self.project_path / '.codebase'
        self.rules = []
        self.gitignore_found = False
        self.watchignore_found = False

        # Store individual pattern sources for reporting
        self.gitignore_patterns = []
        self.watchignore_patterns = []
        self.default_patterns = DEFAULT_IGNORE_PATTERNS.copy()

        # Ensure .codebase directory exists
        ensure_directory(self.codebase_dir)

        # Load rules
        self._load_gitignore()
        self._load_watchignore()

        # Add default patterns
        self._add_default_patterns()

    def _load_gitignore(self):
        """Load rules from .gitignore file if it exists"""
        gitignore_path = self.project_path / '.gitignore'
        if gitignore_path.exists() and gitignore_path.is_file():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_content = f.read()
                    gitignore_lines = gitignore_content.splitlines()
                    # Store raw patterns
                    self.gitignore_patterns = [line for line in gitignore_lines if
                                               line.strip() and not line.strip().startswith('#')]
                    # Create pathspec rule
                    self.rules.append(pathspec.PathSpec.from_lines('gitwildmatch', gitignore_lines))
                self.gitignore_found = True
                print(f"Loaded .gitignore rules from {gitignore_path}")
            except Exception as e:
                print(f"Error loading .gitignore: {e}")

    def _load_watchignore(self):
        """Load rules from .watchignore file in .codebase directory or create it if it doesn't exist"""
        # New location in .codebase directory
        watchignore_path = self.codebase_dir / '.watchignore'

        if watchignore_path.exists() and watchignore_path.is_file():
            try:
                with open(watchignore_path, 'r', encoding='utf-8') as f:
                    watchignore_content = f.read()
                    watchignore_lines = watchignore_content.splitlines()
                    # Store raw patterns
                    self.watchignore_patterns = [line for line in watchignore_lines if
                                                 line.strip() and not line.strip().startswith('#')]
                    # Create pathspec rule
                    self.rules.append(pathspec.PathSpec.from_lines('gitwildmatch', watchignore_lines))
                self.watchignore_found = True
                print(f"Loaded .watchignore rules from {watchignore_path}")
            except Exception as e:
                print(f"Error loading .watchignore: {e}")
        else:
            # Create .watchignore file in .codebase directory
            try:
                with open(watchignore_path, 'w', encoding='utf-8') as f:
                    f.write("# Add your custom ignore patterns here\n")
                    f.write("# Example: *.log\n")
                    f.write("# Example: temp/\n")
                print(f"Created new .watchignore file at {watchignore_path}")
                self.watchignore_patterns = []
            except Exception as e:
                print(f"Error creating .watchignore: {e}")

    def _add_default_patterns(self):
        """Add default ignore patterns"""
        self.rules.append(pathspec.PathSpec.from_lines('gitwildmatch', DEFAULT_IGNORE_PATTERNS))

    def is_ignored(self, path):
        """
        Check if a path should be ignored based on rules.
        Returns True if the path should be ignored.
        """
        # Convert to string path relative to project root
        if isinstance(path, Path):
            rel_path = path.relative_to(self.project_path) if path.is_absolute() else path
            path_str = str(rel_path)
        else:
            # If path is already relative to project root as string
            path_str = path

        # Always ignore the .codebase directory itself
        if path_str == '.codebase' or path_str.startswith('.codebase/'):
            return True

        # Check against all rule sets
        for rule_set in self.rules:
            if rule_set.match_file(path_str):
                return True

        return False

    def get_rule_summary(self):
        """Get a summary of all ignore rules for reporting"""
        rules_info = {
            'gitignore': {
                'found': self.gitignore_found,
                'patterns': self.gitignore_patterns
            },
            'watchignore': {
                'found': self.watchignore_found,
                'patterns': self.watchignore_patterns
            },
            'default': {
                'patterns': self.default_patterns
            }
        }
        return rules_info

    def get_watchignore_path(self):
        """Return the path to the .watchignore file"""
        return self.codebase_dir / '.watchignore'
