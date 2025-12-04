import os
import json
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

SETTINGS_FILENAME = "codebase_tracker_settings.json"

DEFAULT_SETTINGS = {
    "track_only": ["*"],
    "ignore_patterns": DEFAULT_IGNORE_PATTERNS,
    "description": "Configure which files to track or ignore. 'track_only' is an allow-list (default '*' means all). 'ignore_patterns' is a deny-list."
}

class IgnoreRules:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.codebase_dir = self.project_path / '_codebase'
        self.settings_path = self.codebase_dir / SETTINGS_FILENAME

        # Rules
        self.ignore_rules = []
        self.gitignore_found = False
        self.gitignore_patterns = []
        
        self.settings = DEFAULT_SETTINGS.copy()
        self.track_only_spec = None
        self.has_user_defined_only_rules = False

        ensure_directory(self.codebase_dir)

        self._load_gitignore()
        self._load_settings()
        self._compile_rules()

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

    def _load_settings(self):
        """Load settings from JSON file. If it doesn't exist, create it."""
        try:
            if not self.settings_path.exists():
                self._create_default_settings()
            
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                self.settings.update(loaded_settings)
                
        except Exception as e:
            print(f"Error loading or creating {SETTINGS_FILENAME}: {e}")
            # Fallback to defaults if error
            self.settings = DEFAULT_SETTINGS.copy()

    def _create_default_settings(self):
        """Create the default settings file."""
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error creating default settings: {e}")

    def reset_settings(self):
        """Reset settings to default."""
        self.settings = DEFAULT_SETTINGS.copy()
        self._create_default_settings()
        self._compile_rules()

    def _compile_rules(self):
        """Compile pathspecs from settings."""
        # Reset ignore rules (keep gitignore if it was added first? No, ignore_rules list is mixed)
        # Actually, I should rebuild ignore_rules list.
        # But gitignore is added in __init__ before _load_settings.
        # So I should clear ignore_rules and re-add gitignore if I want to be clean, or just append?
        # The current implementation appends.
        # Let's clear and rebuild to be safe in reset_settings, but wait, gitignore is loaded once.
        
        # Better approach:
        self.ignore_rules = []
        if self.gitignore_found:
             # Re-add gitignore rules. I need to store the spec or re-read?
             # I stored gitignore_patterns.
             if self.gitignore_patterns:
                 self.ignore_rules.append(pathspec.PathSpec.from_lines('gitwildmatch', self.gitignore_patterns))

        # Compile ignore patterns from settings
        ignore_patterns = self.settings.get("ignore_patterns", [])
        if ignore_patterns:
            self.ignore_rules.append(pathspec.PathSpec.from_lines('gitwildmatch', ignore_patterns))

        # Compile track_only patterns
        track_only_patterns = self.settings.get("track_only", ["*"])
        
        # If only ["*"], treat as no restriction
        if not track_only_patterns or track_only_patterns == ["*"]:
            self.has_user_defined_only_rules = False
            self.track_only_spec = pathspec.PathSpec.from_lines('gitwildmatch', ["*"])
        else:
            self.has_user_defined_only_rules = True
            self.track_only_spec = pathspec.PathSpec.from_lines('gitwildmatch', track_only_patterns)

    def _normalize_path(self, path):
        if isinstance(path, Path):
            try:
                rel_path = path.relative_to(self.project_path) if path.is_absolute() else path
                return str(rel_path).replace('\\', '/')
            except ValueError:
                # If path is not relative to project_path (should not happen often in this context)
                return str(path).replace('\\', '/')
        return path.replace('\\', '/')

    def is_tracked_by_only_rules(self, path):
        """Check if a path is allowed by track_only rules."""
        if not self.has_user_defined_only_rules:
            return True
        path_str = self._normalize_path(path)
        return self.track_only_spec.match_file(path_str)

    def is_ignored(self, path):
        """Check if a path should be ignored by any ignore rule."""
        path_str = self._normalize_path(path)

        if path_str == '_codebase' or path_str.startswith('_codebase/'):
            return True

        for rule_set in self.ignore_rules:
            if rule_set.match_file(path_str):
                return True

        return False

    def get_rule_summary(self):
        """Get a summary of all rules for reporting"""
        rules_info = {
            'gitignore': {
                'found': self.gitignore_found,
                'patterns': self.gitignore_patterns
            },
            'settings': self.settings
        }
        return rules_info

    def get_settings_path(self):
        """Return the path to the settings file"""
        return self.settings_path
