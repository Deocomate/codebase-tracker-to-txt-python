import os
import time
from pathlib import Path
from file_utils import ensure_directory
from tree_builder import TreeBuilder


class FileCombiner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.output_dir = self.project_path / '.codebase'
        self.output_file = self.output_dir / 'codebase.txt'
        self.tree_builder = TreeBuilder()

        ensure_directory(self.output_dir)

    def combine(self, text_files, ignored_items, ignore_rules, all_files=None, callback=None, cancel_event=None):
        try:
            total_text_files = len(text_files)
            ignored_count = len(ignored_items)
            files_processed = 0
            total_chars = 0
            error_count = 0
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            with open(self.output_file, 'w', encoding='utf-8') as outfile:
                header = f"/* ==========================================================\n" \
                         f"   CODEBASE SNAPSHOT - {timestamp}\n" \
                         f"   Project: {self.project_path.name}\n" \
                         f"   Text Files Included: {total_text_files}\n" \
                         f"   Items Ignored: {ignored_count}\n" \
                         f"   ========================================================== */\n\n"
                outfile.write(header)
                total_chars += len(header)

                if all_files:
                    ignored_dirs = [item for item in ignored_items if item[2] == "directory"]
                    tree_structure = self.tree_builder.build_tree(
                        self.project_path,
                        ignored_dirs,
                        all_files
                    )
                    tree_header = "/* PROJECT STRUCTURE\n" \
                                  f"   {'-' * 60}\n"
                    tree_footer = f"   {'-' * 60} */\n\n"

                    tree_lines = [f"   {line}" for line in tree_structure.split('\n')]
                    formatted_tree = tree_header + '\n'.join(tree_lines) + '\n' + tree_footer
                    outfile.write(formatted_tree)
                    total_chars += len(formatted_tree)

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
                
                if cancel_event and cancel_event.is_set():
                    return False, "Process cancelled by user.", {}

                if ignored_items:
                    rule_summary = ignore_rules.get_rule_summary()
                    ignore_section = "\n/* ===== IGNORED FILES & DIRECTORIES ===== */\n"
                    ignore_section += "/* The following items were excluded from the output. */\n\n"

                    if rule_summary['gitignore']['found']:
                        ignore_section += "/* Based on .gitignore patterns: */\n"
                        for pattern in rule_summary['gitignore']['patterns']:
                            ignore_section += f"/* {pattern} */\n"
                        ignore_section += "\n"

                    # --- UPDATED: Check for 'track_ignore' instead of 'watchignore' ---
                    if rule_summary['track_ignore']['found'] and rule_summary['track_ignore']['patterns']:
                        ignore_section += f"/* Based on {ignore_rules.get_track_ignore_path().name} patterns: */\n"
                        for pattern in rule_summary['track_ignore']['patterns']:
                            ignore_section += f"/* {pattern} */\n"
                        ignore_section += "\n"

                    outfile.write(ignore_section)
                    total_chars += len(ignore_section)

                    ignored_dirs = sorted([item for item in ignored_items if item[2] == "directory"], key=lambda x: x[1])
                    ignored_files_by_rule = sorted([item for item in ignored_items if item[2] == "file"], key=lambda x: x[1])
                    ignored_binary_files = sorted([item for item in ignored_items if item[2] == "binary"], key=lambda x: x[1])

                    if ignored_dirs:
                        outfile.write("/* Ignored directories: */\n")
                        for _, relative_path, _ in ignored_dirs:
                            ignored_line = f"/* {relative_path}/ */\n"
                            outfile.write(ignored_line)
                            total_chars += len(ignored_line)

                    if ignored_files_by_rule:
                        outfile.write("\n/* Ignored files (by rule): */\n")
                        for _, relative_path, _ in ignored_files_by_rule:
                            ignored_line = f"/* {relative_path} */\n"
                            outfile.write(ignored_line)
                            total_chars += len(ignored_line)

                    if ignored_binary_files:
                        outfile.write("\n/* Ignored binary files: */\n")
                        for _, relative_path, _ in ignored_binary_files:
                            ignored_line = f"/* {relative_path} */\n"
                            outfile.write(ignored_line)
                            total_chars += len(ignored_line)

            stats = {
                'text_files': total_text_files,
                'binary_files': len([i for i in ignored_items if i[2] == 'binary']),
                'ignored_items': ignored_count,
                'total_files': total_text_files,
                'total_chars': total_chars,
                'errors': error_count,
                'output_file': str(self.output_file),
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
