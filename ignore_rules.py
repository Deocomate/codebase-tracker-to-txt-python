import os
import json
import pathspec
from pathlib import Path
from file_utils import ensure_directory

# Đổi tên file settings
SETTINGS_FILENAME = "settings.json"

# Cấu trúc mặc định mới
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
        
        # Global rules
        self.gitignore_patterns = []
        self.global_ignore_spec = None
        
        # Config rules: Dictionary { "config_name": { "track": spec, "ignore": spec } }
        self.configs = {}
        
        self.settings = DEFAULT_SETTINGS.copy()
        
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
                self.gitignore_patterns = [line for line in gitignore_lines if line.strip() and not line.strip().startswith('#')]
            except Exception as e:
                print(f"Error loading .gitignore: {e}")

    def _load_settings(self):
        try:
            if not self.settings_path.exists():
                self._create_default_settings()
            
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # Merge loaded settings with default structure ensures keys exist
                self.settings.update(loaded_settings)
                
        except Exception as e:
            print(f"Error loading or creating {SETTINGS_FILENAME}: {e}")
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
        # 1. Compile Global Ignore (Gitignore + Global JSON settings)
        global_patterns = self.gitignore_patterns + self.settings.get("global_ignore_patterns", [])
        self.global_ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', global_patterns)

        # 2. Compile Configs
        self.configs = {}
        track_configs = self.settings.get("track_config", [])
        
        for config in track_configs:
            name = config.get("name", "unnamed")
            tracks = config.get("tracks", ["*"])
            ignores = config.get("ignore_patterns", [])
            
            # Normalize tracks: if user inputs "/app", ensure it matches contents
            # gitwildmatch handles directories, but we ensure robustness
            
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
        """Check if path matches global ignore rules (including .gitignore)"""
        path_str = self._normalize_path(path)
        if path_str == '_codebase' or path_str.startswith('_codebase/'):
            return True
        return self.global_ignore_spec.match_file(path_str)

    def get_matching_configs(self, path):
        """
        Returns a list of config names that want to track this file.
        Logic: Not globally ignored AND (Matches Track Spec AND Not Matches Config Ignore Spec)
        """
        if self.is_globally_ignored(path):
            return []

        path_str = self._normalize_path(path)
        matching_config_names = []

        for name, specs in self.configs.items():
            track_spec = specs["track_spec"]
            ignore_spec = specs["ignore_spec"]

            # Must match track pattern
            if track_spec.match_file(path_str):
                # Must NOT match specific ignore pattern
                if ignore_spec and ignore_spec.match_file(path_str):
                    continue
                matching_config_names.append(name)
        
        return matching_config_names

    def get_settings_path(self):
        return self.settings_path
