"""Abstract base class for all formatters."""

from abc import ABC, abstractmethod
from pathlib import Path
from app.utils.file_utils import detect_encoding


class BaseFormatter(ABC):
    """Base class defining the interface for all export formatters."""

    COMMENT_MARKERS = {
        ".py": "#",
        ".sh": "#",
        ".rb": "#",
        ".yml": "#",
        ".yaml": "#",
        ".js": "//",
        ".ts": "//",
        ".tsx": "//",
        ".jsx": "//",
        ".java": "//",
        ".c": "//",
        ".cpp": "//",
        ".h": "//",
        ".cs": "//",
        ".go": "//",
        ".rs": "//",
        ".swift": "//",
        ".kt": "//",
    }

    def __init__(self, strip_comments: bool = True):
        self.strip_comments = strip_comments

    @abstractmethod
    def get_extension(self) -> str:
        """Return the file extension for this format (e.g., 'txt', 'json')."""
        pass

    @abstractmethod
    def format_output(self, config_name: str, timestamp: str, files: list) -> str:
        """
        Format the complete output for a config.

        Args:
            config_name: Name of the configuration
            timestamp: Generation timestamp
            files: List of (abs_path, rel_path) tuples

        Returns:
            Formatted string ready to write to file
        """
        pass

    def write_output(self, file_handle, config_name: str, timestamp: str, files: list) -> int:
        """
        Stream formatted output directly to a file handle.
        Returns total characters written.
        """
        content = self.format_output(config_name, timestamp, files)
        file_handle.write(content)
        return len(content)

    def _read_file_content(self, abs_path: str, rel_path: str) -> str:
        """Read and optionally strip comments from file content."""
        try:
            encoding = detect_encoding(abs_path)
            comment_marker = (
                self.COMMENT_MARKERS.get(Path(rel_path).suffix.lower())
                if self.strip_comments
                else None
            )

            with open(abs_path, "r", encoding=encoding, errors="replace") as text_file:
                lines = []
                for line in text_file:
                    if self._should_skip_line(line, comment_marker):
                        continue
                    lines.append(line.rstrip("\n\r"))
                return "\n".join(lines)
        except Exception as e:
            return f"ERROR: Could not read file: {e}"

    def _should_skip_line(self, line: str, comment_marker: str | None) -> bool:
        """Check if line should be skipped (empty or comment)."""
        stripped = line.strip()
        if not stripped:
            return True
        if comment_marker and stripped.startswith(comment_marker):
            return True
        return False

    def _get_language_from_extension(self, rel_path: str) -> str:
        """Get programming language name from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".jsx": "jsx",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".rb": "ruby",
            ".php": "php",
            ".sh": "bash",
            ".ps1": "powershell",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".less": "less",
            ".sql": "sql",
            ".md": "markdown",
            ".vue": "vue",
            ".svelte": "svelte",
        }
        suffix = Path(rel_path).suffix.lower()
        return ext_map.get(suffix, "")
