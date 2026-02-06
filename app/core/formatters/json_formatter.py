"""JSON formatter - structured output for programmatic consumption."""

import json
from app.core.formatters.base_formatter import BaseFormatter


class JsonFormatter(BaseFormatter):
    """Format output as JSON with metadata and files array."""

    def get_extension(self) -> str:
        return "json"

    def format_output(self, config_name: str, timestamp: str, files: list) -> str:
        output = {
            "metadata": {
                "config": config_name,
                "files_count": len(files),
                "generated_at": timestamp,
            },
            "files": [],
        }

        for abs_path, rel_path in files:
            content = self._read_file_content(abs_path, rel_path)
            language = self._get_language_from_extension(rel_path)

            file_entry = {
                "path": rel_path.replace("\\", "/"),
                "language": language,
                "content": content,
            }
            output["files"].append(file_entry)

        return json.dumps(output, ensure_ascii=False, indent=2)
