"""Markdown formatter - readable output with syntax highlighting."""

from app.core.formatters.base_formatter import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """Format output as Markdown with fenced code blocks."""

    def get_extension(self) -> str:
        return "md"

    def format_output(self, config_name: str, timestamp: str, files: list) -> str:
        lines = []
        lines.append(f"# {config_name}")
        lines.append("")
        lines.append(f"> Generated: {timestamp} | Files: {len(files)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        for abs_path, rel_path in files:
            content = self._read_file_content(abs_path, rel_path)
            language = self._get_language_from_extension(rel_path)

            # File header
            normalized_path = rel_path.replace("\\", "/")
            lines.append(f"## `{normalized_path}`")
            lines.append("")

            # Code block with syntax highlighting
            lines.append(f"```{language}")
            lines.append(content)
            lines.append("```")
            lines.append("")

        return "\n".join(lines)
