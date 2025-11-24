import time
import json
import io
import hashlib
from pathlib import Path
from file_utils import ensure_directory
from tree_builder import TreeBuilder


class FileCombiner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.output_dir = self.project_path / '_codebase'
        self.output_file = self.output_dir / 'codebase.txt'
        self.structure_file = self.output_dir / 'codebase_structure.txt'
        self.tree_builder = TreeBuilder()

        ensure_directory(self.output_dir)

        self.comment_markers = {
            '.py': '#', '.sh': '#', '.rb': '#', '.yml': '#', '.yaml': '#',
            '.js': '//', '.ts': '//', '.java': '//', '.c': '//', '.cpp': '//', '.h': '//',
            '.cs': '//', '.go': '//', '.rs': '//', '.swift': '//', '.kt': '//'
        }

    def _should_skip_line(self, line, comment_marker):
        stripped_line = line.strip()
        if not stripped_line:
            return True

        if comment_marker and stripped_line.startswith(comment_marker):
            return True

        return False

    def _write_streaming_content(self, text_stream, outfile, comment_marker):
        original_lines = 0
        optimized_lines = 0
        optimized_chars = 0

        for raw_line in text_stream:
            original_lines += 1

            if self._should_skip_line(raw_line, comment_marker):
                continue

            if raw_line.endswith('\n'):
                outfile.write(raw_line)
                line_length = len(raw_line)
            else:
                outfile.write(raw_line + '\n')
                line_length = len(raw_line) + 1

            optimized_lines += 1
            optimized_chars += line_length

        return original_lines, optimized_lines, optimized_chars

    def _optimize_content(self, content, file_path):
        """
        Removes blank lines and full-line comments to reduce token count.
        This is a safe optimization that preserves indentation and inline comments.
        """
        file_ext = Path(file_path).suffix.lower()
        comment_marker = self.comment_markers.get(file_ext)

        lines = content.splitlines()
        optimized_lines = []

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue

            if comment_marker and stripped_line.startswith(comment_marker):
                continue

            optimized_lines.append(line)

        return "\n".join(optimized_lines)

    def combine(self, text_files, ignored_items, ignore_rules, all_files=None, callback=None, cancel_event=None):
        try:
            total_text_files = len(text_files)
            ignored_count = len(ignored_items)
            files_processed = 0
            total_chars = 0
            error_count = 0
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            files_processed = 0
            total_chars = 0
            error_count = 0
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            # 1. Generate and write directory structure to codebase_structure.txt
            if all_files:
                ignored_dirs = [item for item in ignored_items if item[2] == "directory"]
                tree_structure = self.tree_builder.build_tree(
                    self.project_path,
                    ignored_dirs,
                    all_files
                )
                
                with open(self.structure_file, 'w', encoding='utf-8') as struct_file:
                    struct_header = f"/* ==========================================================\n" \
                                    f"   PROJECT STRUCTURE - {timestamp}\n" \
                                    f"   Project: {self.project_path.name}\n" \
                                    f"   ========================================================== */\n\n"
                    struct_file.write(struct_header)
                    struct_file.write(tree_structure)

            # 2. Generate and write code content to codebase.txt
            with open(self.output_file, 'w', encoding='utf-8') as outfile:
                header = f"/* ==========================================================\n" \
                         f"   CODEBASE SNAPSHOT - {timestamp}\n" \
                         f"   Project: {self.project_path.name}\n" \
                         f"   Text Files Included: {total_text_files}\n" \
                         f"   Items Ignored: {ignored_count}\n" \
                         f"   Structure File: codebase_structure.txt\n" \
                         f"   ========================================================== */\n\n"
                outfile.write(header)
                total_chars += len(header)

                for absolute_path, relative_path in text_files:
                    if cancel_event and cancel_event.is_set():
                        if callback:
                            callback("Combine process cancelled.", -1)
                        break

                    files_processed += 1
                    if callback:
                        callback(f"Processing ({files_processed}/{total_text_files}): {relative_path}",
                                 0.5 + (files_processed / total_text_files) * 0.5)

                    try:
                        comment_marker = self.comment_markers.get(Path(relative_path).suffix.lower())
                        hasher = hashlib.sha256()

                        with open(absolute_path, 'rb') as raw_file:
                            for chunk in iter(lambda: raw_file.read(1048576), b''):
                                hasher.update(chunk)
                            raw_file.seek(0)

                            text_stream = io.TextIOWrapper(raw_file, encoding='utf-8', errors='replace')
                            try:
                                file_header = f"/* ===== {relative_path} ===== */\n"
                                outfile.write(file_header)
                                original_lines, optimized_lines, optimized_chars = self._write_streaming_content(
                                    text_stream, outfile, comment_marker
                                )
                            finally:
                                text_stream.detach()

                        outfile.write("\n\n")

                        skipped_lines = max(original_lines - optimized_lines, 0)
                        
                        total_chars += len(file_header) + optimized_chars + 2
                    except Exception as e:
                        error_count += 1
                        error_msg = f"/* ===== ERROR: Could not read file: {relative_path} ===== */\n/* {str(e)} */\n\n"
                        outfile.write(error_msg)
                        total_chars += len(error_msg)

                if cancel_event and cancel_event.is_set():
                    return False, "Process cancelled by user.", {}

            stats = {
                'text_files': total_text_files,
                'binary_files': len([i for i in ignored_items if i[2] == 'binary']),
                'ignored_items': ignored_count,
                'total_files': total_text_files,
                'total_chars': total_chars,
                'errors': error_count,
                'output_file': str(self.output_file),
                'structure_file': str(self.structure_file),
                'timestamp': timestamp
            }

            if callback:
                callback(f"Done! Combined {total_text_files} text files into {self.output_file.name}", 1.0)

            return True, f"Successfully combined {total_text_files} text files.", stats

        except Exception as e:
            error_msg = f"Error combining files: {str(e)}"
            if callback:
                callback(error_msg, 1.0)
            return False, error_msg, {}