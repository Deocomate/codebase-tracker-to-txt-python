"""TXT formatter - maintains backward compatibility with original output."""

from app.core.formatters.base_formatter import BaseFormatter


class TxtFormatter(BaseFormatter):
    """Format output as plain text (original format)."""

    def get_extension(self) -> str:
        return "txt"

    def format_output(self, config_name: str, timestamp: str, files: list) -> str:
        lines = []
        lines.append(f"# {config_name} | {len(files)} files | {timestamp}\n")

        for abs_path, rel_path in files:
            content = self._read_file_content(abs_path, rel_path)
            lines.append(f"// {rel_path}")
            lines.append(content)
            lines.append("")  # Empty line between files

        return "\n".join(lines)
