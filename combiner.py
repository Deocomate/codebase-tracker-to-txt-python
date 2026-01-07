import os
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

    def combine(self, categorized_files, ignored_items, ignore_rules, all_files=None, callback=None, cancel_event=None):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        generated_files = []
        
        # 1. Generate Structure File (Global)
        if all_files:
            if callback: callback("Generating structure tree...", 0.1)
            # Filter ignored dirs for tree visual
            ignored_dirs = [item for item in ignored_items 
                           if item[2] == "global_ignore" and os.path.exists(item[0]) and os.path.isdir(item[0])]
            
            tree_structure = self.tree_builder.build_tree(self.project_path, ignored_dirs, all_files)
            
            with open(self.structure_file, 'w', encoding='utf-8') as struct_file:
                struct_header = (f"/* ==========================================================\n"
                                 f"   PROJECT STRUCTURE - {timestamp}\n"
                                 f"   Project: {self.project_path.name}\n"
                                 f"   ========================================================== */\n\n")
                struct_file.write(struct_header)
                struct_file.write(tree_structure)
            generated_files.append(str(self.structure_file.name))

        # 2. Generate Text Files for each Config
        total_configs = len(categorized_files)
        current_config_idx = 0
        total_stats = {'files_created': [], 'total_chars': 0, 'total_files_included': 0}

        for config_name, text_files in categorized_files.items():
            current_config_idx += 1
            if not text_files:
                continue  # Skip empty configs
            
            output_filename = f"{config_name}.txt"
            output_file_path = self.output_dir / output_filename
            
            if callback: 
                callback(f"Generating {output_filename} ({len(text_files)} files)...", 
                         0.2 + (current_config_idx / total_configs) * 0.8)

            try:
                with open(output_file_path, 'w', encoding='utf-8') as outfile:
                    header = (f"/* ==========================================================\n"
                              f"   CODEBASE SNAPSHOT - {timestamp}\n"
                              f"   Config Group: {config_name}\n"
                              f"   Files Included: {len(text_files)}\n"
                              f"   ========================================================== */\n\n")
                    outfile.write(header)
                    
                    for absolute_path, relative_path in text_files:
                        if cancel_event and cancel_event.is_set():
                            return False, "Cancelled", {}
                        
                        try:
                            comment_marker = self.comment_markers.get(Path(relative_path).suffix.lower())
                            with open(absolute_path, 'rb') as raw_file:
                                text_stream = io.TextIOWrapper(raw_file, encoding='utf-8', errors='replace')
                                try:
                                    file_header = f"/* ===== {relative_path} ===== */\n"
                                    outfile.write(file_header)
                                    _, _, chars = self._write_streaming_content(text_stream, outfile, comment_marker)
                                    total_stats['total_chars'] += chars
                                finally:
                                    text_stream.detach()
                            outfile.write("\n\n")
                        except Exception as e:
                            outfile.write(f"/* ERROR reading {relative_path}: {e} */\n\n")

                generated_files.append(output_filename)
                total_stats['files_created'].append(output_filename)
                total_stats['total_files_included'] += len(text_files)

            except Exception as e:
                print(f"Error creating {output_filename}: {e}")

        stats = {
            'generated_files': generated_files,
            'output_dir': str(self.output_dir),
            'structure_file': str(self.structure_file),
            'total_chars': total_stats['total_chars'],
            'total_files_included': total_stats['total_files_included'],
            'ignored_items': len(ignored_items),
            'summary': f"Created {len(generated_files)} files with {total_stats['total_files_included']} source files."
        }
        
        return True, "Process Complete", stats