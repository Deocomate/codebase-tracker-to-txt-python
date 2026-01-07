import os
import time
import io
from pathlib import Path
from app.utils.file_utils import ensure_directory
from app.core.tree_builder import TreeBuilder

# Comment markers for stripping comments from output
COMMENT_MARKERS = {
    '.py': '#', '.sh': '#', '.rb': '#', '.yml': '#', '.yaml': '#',
    '.js': '//', '.ts': '//', '.tsx': '//', '.jsx': '//',
    '.java': '//', '.c': '//', '.cpp': '//', '.h': '//',
    '.cs': '//', '.go': '//', '.rs': '//', '.swift': '//', '.kt': '//'
}


class FileCombiner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.output_dir = self.project_path / '_codebase'
        self.structure_file = self.output_dir / 'codebase_structure.txt'
        self.tree_builder = TreeBuilder()
        ensure_directory(self.output_dir)

    def _should_skip_line(self, line, comment_marker):
        """Skip empty lines and single-line comments."""
        stripped = line.strip()
        if not stripped:
            return True
        if comment_marker and stripped.startswith(comment_marker):
            return True
        return False

    def _write_content(self, text_stream, outfile, comment_marker):
        """Write file content, optionally stripping comments."""
        chars = 0
        for raw_line in text_stream:
            if self._should_skip_line(raw_line, comment_marker):
                continue
            if raw_line.endswith('\n'):
                outfile.write(raw_line)
                chars += len(raw_line)
            else:
                outfile.write(raw_line + '\n')
                chars += len(raw_line) + 1
        return chars

    def combine(self, categorized_files, ignored_items, ignore_rules, all_files=None, callback=None, cancel_event=None):
        """Combine files into output txt files."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        generated_files = []
        
        # Generate structure file
        if all_files:
            if callback:
                callback("Generating structure tree...", 0.1)
            ignored_dirs = [item for item in ignored_items 
                           if item[2] == "global_ignore" and os.path.exists(item[0]) and os.path.isdir(item[0])]
            
            tree = self.tree_builder.build_tree(self.project_path, ignored_dirs, all_files)
            
            with open(self.structure_file, 'w', encoding='utf-8') as f:
                f.write(f"# {self.project_path.name} | Structure | {timestamp}\n\n")
                f.write(tree)
            generated_files.append(str(self.structure_file.name))

        # Generate config output files
        total_configs = len(categorized_files)
        total_stats = {'total_chars': 0, 'total_files_included': 0}

        for idx, (config_name, text_files) in enumerate(categorized_files.items(), 1):
            if not text_files:
                continue
            
            output_filename = f"{config_name}.txt"
            output_path = self.output_dir / output_filename
            
            if callback:
                callback(f"Generating {output_filename} ({len(text_files)} files)...", 
                         0.2 + (idx / total_configs) * 0.8)

            try:
                with open(output_path, 'w', encoding='utf-8') as outfile:
                    # Minimal header for token efficiency
                    outfile.write(f"# {config_name} | {len(text_files)} files | {timestamp}\n\n")
                    
                    for abs_path, rel_path in text_files:
                        if cancel_event and cancel_event.is_set():
                            return False, "Cancelled", {}
                        
                        try:
                            comment_marker = COMMENT_MARKERS.get(Path(rel_path).suffix.lower())
                            with open(abs_path, 'rb') as raw_file:
                                text_stream = io.TextIOWrapper(raw_file, encoding='utf-8', errors='replace')
                                try:
                                    # Minimal file header
                                    outfile.write(f"// {rel_path}\n")
                                    chars = self._write_content(text_stream, outfile, comment_marker)
                                    total_stats['total_chars'] += chars
                                finally:
                                    text_stream.detach()
                            outfile.write("\n")
                        except Exception as e:
                            outfile.write(f"// ERROR: {rel_path}: {e}\n\n")

                generated_files.append(output_filename)
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
