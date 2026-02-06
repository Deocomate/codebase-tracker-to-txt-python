"""XML formatter - structured output for enterprise/integration use."""

import xml.sax.saxutils as saxutils
from app.core.formatters.base_formatter import BaseFormatter


class XmlFormatter(BaseFormatter):
    """Format output as well-formed XML with CDATA sections."""

    def get_extension(self) -> str:
        return "xml"

    def format_output(self, config_name: str, timestamp: str, files: list) -> str:
        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')

        # Root element with attributes
        escaped_config = saxutils.escape(config_name)
        lines.append(
            f'<codebase config="{escaped_config}" files="{len(files)}" generated="{timestamp}">'
        )

        for abs_path, rel_path in files:
            content = self._read_file_content(abs_path, rel_path)
            language = self._get_language_from_extension(rel_path)

            # Escape path for attribute
            normalized_path = rel_path.replace("\\", "/")
            escaped_path = saxutils.escape(normalized_path)

            # Use CDATA to preserve content without escaping
            # Handle edge case where content contains "]]>"
            safe_content = content.replace("]]>", "]]]]><![CDATA[>")

            lines.append(
                f'  <file path="{escaped_path}" language="{language}"><![CDATA[{safe_content}]]></file>'
            )

        lines.append("</codebase>")

        return "\n".join(lines)
