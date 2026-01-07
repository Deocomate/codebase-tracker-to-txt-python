import os
import json
import pathspec
from pathlib import Path
from app.utils.file_utils import ensure_directory

SETTINGS_FILENAME = "settings.json"

DEFAULT_SETTINGS = {
    "track_config": [
        {
            "name": "codebase",
            "tracks": ["*"],
            "ignore_patterns": []
        }
    ],
    "global_ignore_patterns": [
        '.git/', 'node_modules/', 'vendor/', 'bower_components/', 'storage/',
        'build/', 'dist/', 'out/', 'target/', '.svn/', '.hg/', '.bzr/', '.idea/',
        '.vscode/', '.project/', '.settings/', '__pycache__/', '.pytest_cache/',
        '.mypy_cache/', '.ruff_cache/', 'coverage/', 'logs/', 'tmp/', 'temp/',
        '*.lockb', '*.log', '*.tmp', '*.bak', '*.swp', '*.DS_Store'
    ],
    "description": "Configure multiple output files based on track patterns."
}


class IgnoreRules:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.codebase_dir = self.project_path / '_codebase'
        self.settings_path = self.codebase_dir / SETTINGS_FILENAME
        
        self.gitignore_patterns = []
        self.global_ignore_spec = None
        self.configs = {}
        self.settings = DEFAULT_SETTINGS.copy()
        
        ensure_directory(self.codebase_dir)
        self._load_gitignore()
        self._load_settings()
        self._compile_rules()

    def _load_gitignore(self):
        """Load rules from .gitignore file if it exists."""
        gitignore_path = self.project_path / '.gitignore'
        if gitignore_path.exists() and gitignore_path.is_file():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    lines = f.read().splitlines()
                self.gitignore_patterns = [l for l in lines if l.strip() and not l.strip().startswith('#')]
            except Exception as e:
                print(f"Error loading .gitignore: {e}")

    def _load_settings(self):
        try:
            if not self.settings_path.exists():
                self._create_default_settings()
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                self.settings.update(loaded)
        except Exception as e:
            print(f"Error loading {SETTINGS_FILENAME}: {e}")
            self.settings = DEFAULT_SETTINGS.copy()

    def _create_default_settings(self):
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_SETTINGS, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error creating default settings: {e}")

    def reset_settings(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self._create_default_settings()
        self._compile_rules()

    def _compile_rules(self):
        """Compile pathspecs from settings."""
        global_patterns = self.gitignore_patterns + self.settings.get("global_ignore_patterns", [])
        self.global_ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', global_patterns)

        self.configs = {}
        for config in self.settings.get("track_config", []):
            name = config.get("name", "unnamed")
            tracks = config.get("tracks", ["*"])
            ignores = config.get("ignore_patterns", [])
            
            self.configs[name] = {
                "track_spec": pathspec.PathSpec.from_lines('gitwildmatch', tracks),
                "ignore_spec": pathspec.PathSpec.from_lines('gitwildmatch', ignores) if ignores else None
            }

    def _normalize_path(self, path):
        if isinstance(path, Path):
            try:
                rel_path = path.relative_to(self.project_path) if path.is_absolute() else path
                return str(rel_path).replace('\\', '/')
            except ValueError:
                return str(path).replace('\\', '/')
        return path.replace('\\', '/')

    def is_globally_ignored(self, path):
        """Check if path matches global ignore rules."""
        path_str = self._normalize_path(path)
        if path_str == '_codebase' or path_str.startswith('_codebase/'):
            return True
        return self.global_ignore_spec.match_file(path_str)

    def get_matching_configs(self, path):
        """Returns a list of config names that want to track this file."""
        if self.is_globally_ignored(path):
            return []

        path_str = self._normalize_path(path)
        matching = []

        for name, specs in self.configs.items():
            if specs["track_spec"].match_file(path_str):
                if specs["ignore_spec"] and specs["ignore_spec"].match_file(path_str):
                    continue
                matching.append(name)
        
        return matching

    def get_settings_path(self):
        return self.settings_path
