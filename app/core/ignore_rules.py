import os
import json
import pathspec
from pathlib import Path
from app.utils.file_utils import ensure_directory

SETTINGS_FILENAME = "settings.json"

DEFAULT_SETTINGS = {
    "track_config": [{"name": "codebase", "tracks": ["*"], "ignore_patterns": []}],
    "global_ignore_patterns": [
        ".git/",
        "node_modules/",
        "vendor/",
        "bower_components/",
        "storage/",
        "build/",
        "dist/",
        "out/",
        "target/",
        ".svn/",
        ".hg/",
        ".bzr/",
        ".idea/",
        ".vscode/",
        ".project/",
        ".settings/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        "coverage/",
        "logs/",
        "tmp/",
        "temp/",
        "*.lockb",
        "*.log",
        "*.tmp",
        "*.bak",
        "*.swp",
        "*.DS_Store",
    ],
    "description": "Configure multiple output files based on track patterns.",
}


class IgnoreRules:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.codebase_dir = self.project_path / "_codebase"
        self.settings_path = self.codebase_dir / SETTINGS_FILENAME

        self.gitignore_patterns = []
        # Tách biệt spec: User Settings (Cứng) và Gitignore (Mềm)
        self.user_ignore_spec = None
        self.gitignore_spec = None

        self.configs = {}
        self.settings = DEFAULT_SETTINGS.copy()

        ensure_directory(self.codebase_dir)
        self._load_gitignore()
        self._load_settings()
        self._compile_rules()

    def _load_gitignore(self):
        """Load rules from .gitignore file if it exists."""
        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists() and gitignore_path.is_file():
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    self.gitignore_patterns = f.read().splitlines()
            except Exception as e:
                print(f"Error loading .gitignore: {e}")

    def _load_settings(self):
        try:
            if not self.settings_path.exists():
                self._create_default_settings()

            with open(self.settings_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.settings.update(loaded)
        except Exception as e:
            print(f"Error loading {SETTINGS_FILENAME}: {e}")
            self.settings = DEFAULT_SETTINGS.copy()

    def _create_default_settings(self):
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error creating default settings: {e}")

    def reset_settings(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self._create_default_settings()
        self._compile_rules()

    def _compile_rules(self):
        """Compile pathspecs from settings using gitwildmatch logic."""
        # 1. User Settings Ignore Rules (Mức ưu tiên cao nhất - Chặn tuyệt đối)
        user_patterns = self.settings.get("global_ignore_patterns", [])
        self.user_ignore_spec = pathspec.PathSpec.from_lines(
            "gitwildmatch", user_patterns
        )

        # 2. Gitignore Rules (Mức ưu tiên thấp hơn - Có thể bị override bởi track)
        if self.gitignore_patterns:
            self.gitignore_spec = pathspec.PathSpec.from_lines(
                "gitwildmatch", self.gitignore_patterns
            )
        else:
            self.gitignore_spec = None

        # 3. Compile Configs (Track patterns)
        self.configs = {}
        for config in self.settings.get("track_config", []):
            name = config.get("name", "unnamed")
            tracks = config.get("tracks", ["*"])
            ignores = config.get("ignore_patterns", [])

            self.configs[name] = {
                "track_spec": pathspec.PathSpec.from_lines("gitwildmatch", tracks),
                "ignore_spec": (
                    pathspec.PathSpec.from_lines("gitwildmatch", ignores)
                    if ignores
                    else None
                ),
            }

    def _normalize_path(self, path):
        """
        Convert path to POSIX style (forward slashes) relative to project root.
        """
        if isinstance(path, Path):
            try:
                if path.is_absolute():
                    rel_path = path.relative_to(self.project_path)
                    return str(rel_path).replace(os.sep, "/")
                return str(path).replace(os.sep, "/")
            except ValueError:
                return str(path).replace(os.sep, "/")
        return str(path).replace(os.sep, "/")

    def is_globally_ignored(self, path, is_dir=False):
        """
        Check if path should be ignored.
        Logic:
        1. Nếu nằm trong settings.json 'global_ignore_patterns' -> BỎ QUA LUÔN (Ví dụ: node_modules)
        2. Nếu nằm trong .gitignore -> Kiểm tra xem user có 'track' nó không?
           - Nếu có config nào track nó -> LẤY (Override .gitignore)
           - Nếu không ai track -> BỎ QUA
        """
        path_str = self._normalize_path(path)

        # Luôn bỏ qua folder nội bộ _codebase
        if path_str == "_codebase" or path_str.startswith("_codebase/"):
            return True

        check_path = path_str
        if is_dir and not check_path.endswith("/"):
            check_path += "/"

        # 1. Kiểm tra Global Settings (Cấm tuyệt đối)
        # Các file như node_modules, .git sẽ bị chặn ở đây
        if self.user_ignore_spec.match_file(check_path):
            return True

        # 2. Kiểm tra Gitignore (Có thể "khoan hồng" nếu được Track)
        if self.gitignore_spec and self.gitignore_spec.match_file(check_path):
            # File này nằm trong .gitignore. Nhưng user có muốn track nó không?
            is_tracked_by_any = False

            # Duyệt qua tất cả các configs để xem có ai "tracks" file này không
            for config in self.configs.values():
                if config["track_spec"].match_file(path_str):
                    # Có config muốn track file này -> Không ignore nữa
                    is_tracked_by_any = True
                    break

            # Nếu được track -> False (Không ignore)
            if is_tracked_by_any:
                return False

            # Nếu không được track -> True (Ignore theo gitignore)
            return True

        return False

    def get_matching_configs(self, path):
        """Returns a list of config names that want to track this file."""
        # Lưu ý: is_globally_ignored đã được gọi ở Scanner trước khi gọi hàm này,
        # nhưng ta vẫn gọi lại hoặc check logic ở đây để đảm bảo tính nhất quán.
        if self.is_globally_ignored(path, is_dir=False):
            return []

        path_str = self._normalize_path(path)
        matching = []

        for name, specs in self.configs.items():
            if specs["track_spec"].match_file(path_str):
                # Check config-specific ignores
                if specs["ignore_spec"] and specs["ignore_spec"].match_file(path_str):
                    continue
                matching.append(name)

        return matching

    def get_settings_path(self):
        return self.settings_path
