import os
import time
from pathlib import Path
from file_utils import ensure_directory


class FileCombiner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.output_dir = self.project_path / '.codebase'
        self.output_file = self.output_dir / 'codebase.txt'

        # Ensure output directory exists
        ensure_directory(self.output_dir)

    def combine(self, text_files, binary_files, ignored_items, ignore_rules, callback=None):
        """
        Combine text files into a single output file.
        Text files are included with their content, binary files just have their paths listed.
        Ignored items are listed in a separate section.

        Args:
            text_files: List of tuples (absolute_path, relative_path) for text files
            binary_files: List of tuples (absolute_path, relative_path) for binary files
            ignored_items: List of tuples (absolute_path, relative_path, type) for ignored items
            ignore_rules: IgnoreRules object with pattern information
            callback: Optional callback function for progress updates

        Returns:
            Tuple of (success, message, stats)
        """
        try:
            total_files = len(text_files) + len(binary_files)
            ignored_count = len(ignored_items)
            files_processed = 0
            total_chars = 0
            error_count = 0
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            with open(self.output_file, 'w', encoding='utf-8') as outfile:
                # Write header
                header = f"/* ==========================================================\n" \
                         f"   CODEBASE SNAPSHOT - {timestamp}\n" \
                         f"   Project: {self.project_path.name}\n" \
                         f"   Files: {total_files} ({len(text_files)} text, {len(binary_files)} binary)\n" \
                         f"   Ignored Items: {ignored_count}\n" \
                         f"   ========================================================== */\n\n"
                outfile.write(header)
                total_chars += len(header)

                # Process text files
                for absolute_path, relative_path in text_files:
                    files_processed += 1
                    if callback:
                        callback(f"Processing ({files_processed}/{total_files}): {relative_path}",
                                 files_processed / total_files)

                    try:
                        with open(absolute_path, 'r', encoding='utf-8', errors='replace') as infile:
                            content = infile.read()

                            file_header = f"/* ===== {relative_path} ===== */\n"
                            outfile.write(file_header)
                            outfile.write(content)
                            outfile.write("\n\n")

                            total_chars += len(file_header) + len(content) + 2
                    except Exception as e:
                        error_count += 1
                        error_msg = f"/* ===== ERROR: Could not read file: {relative_path} ===== */\n/* {str(e)} */\n\n"
                        outfile.write(error_msg)
                        total_chars += len(error_msg)

                # List binary files
                if binary_files:
                    binary_section = "\n/* ===== BINARY FILES (PATHS ONLY) ===== */\n"
                    outfile.write(binary_section)
                    total_chars += len(binary_section)

                    for _, relative_path in binary_files:
                        files_processed += 1
                        binary_line = f"/* Binary file: {relative_path} */\n"
                        outfile.write(binary_line)
                        total_chars += len(binary_line)

                        if callback and files_processed % 10 == 0:
                            callback(f"Listing binary files ({files_processed}/{total_files})",
                                     files_processed / total_files)

                # Add ignored items section
                if ignored_items:
                    # Get rule summary for reference
                    rule_summary = ignore_rules.get_rule_summary()

                    ignore_section = "\n/* ===== IGNORED FILES & DIRECTORIES ===== */\n"
                    ignore_section += "/* The following items were excluded based on ignore rules */\n\n"

                    # Add info about gitignore
                    if rule_summary['gitignore']['found']:
                        ignore_section += "/* .gitignore patterns: */\n"
                        for pattern in rule_summary['gitignore']['patterns']:
                            ignore_section += f"/*   {pattern} */\n"
                        ignore_section += "\n"

                    # Add info about watchignore
                    if rule_summary['watchignore']['found'] and rule_summary['watchignore']['patterns']:
                        ignore_section += "/* .watchignore patterns: */\n"
                        for pattern in rule_summary['watchignore']['patterns']:
                            ignore_section += f"/*   {pattern} */\n"
                        ignore_section += "\n"

                    # Add the ignored items list
                    ignore_section += "/* Ignored items list: */\n"
                    outfile.write(ignore_section)
                    total_chars += len(ignore_section)

                    # Group ignored items by type for better organization
                    ignored_dirs = [item for item in ignored_items if item[2] == "directory"]
                    ignored_files = [item for item in ignored_items if item[2] == "file"]

                    # List directories first
                    if ignored_dirs:
                        outfile.write("/* Ignored directories: */\n")
                        for _, relative_path, _ in sorted(ignored_dirs, key=lambda x: x[1]):
                            ignored_line = f"/*   {relative_path}/ */\n"
                            outfile.write(ignored_line)
                            total_chars += len(ignored_line)

                    # Then list individual files
                    if ignored_files:
                        outfile.write("\n/* Ignored files: */\n")
                        for _, relative_path, _ in sorted(ignored_files, key=lambda x: x[1]):
                            ignored_line = f"/*   {relative_path} */\n"
                            outfile.write(ignored_line)
                            total_chars += len(ignored_line)

            stats = {
                'text_files': len(text_files),
                'binary_files': len(binary_files),
                'ignored_items': ignored_count,
                'total_files': total_files,
                'total_chars': total_chars,
                'errors': error_count,
                'output_file': str(self.output_file),
                'timestamp': timestamp
            }

            if callback:
                callback(f"Done! Combined {len(text_files)} text files into {self.output_file}", 1.0)

            return True, f"Successfully combined {len(text_files)} text files into {self.output_file}", stats

        except Exception as e:
            error_msg = f"Error combining files: {str(e)}"
            if callback:
                callback(error_msg, 1.0)
            return False, error_msg, {}
