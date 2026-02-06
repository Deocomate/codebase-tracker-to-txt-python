"""
Formatters module for multi-format codebase export.
Supports: TXT, JSON, Markdown, XML
"""

from app.core.formatters.base_formatter import BaseFormatter
from app.core.formatters.txt_formatter import TxtFormatter
from app.core.formatters.json_formatter import JsonFormatter
from app.core.formatters.markdown_formatter import MarkdownFormatter
from app.core.formatters.xml_formatter import XmlFormatter

FORMATTERS = {
    "txt": TxtFormatter,
    "json": JsonFormatter,
    "md": MarkdownFormatter,
    "xml": XmlFormatter,
}

__all__ = [
    "BaseFormatter",
    "TxtFormatter",
    "JsonFormatter",
    "MarkdownFormatter",
    "XmlFormatter",
    "FORMATTERS",
]
