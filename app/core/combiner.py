import os
import time
from pathlib import Path
from app.utils.file_utils import ensure_directory
from app.core.tree_builder import TreeBuilder
from app.core.formatters import FORMATTERS


class FileCombiner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.output_dir = self.project_path / "_codebase"
        self.structure_file = self.output_dir / "codebase_structure.txt"
        self.tree_builder = TreeBuilder()
        ensure_directory(self.output_dir)

    def combine(
        self,
        categorized_files,
        ignored_items,
        ignore_rules,
        all_files=None,
        callback=None,
        cancel_event=None,
        export_formats=None,
    ):
        """Combine files into output files in selected formats."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        generated_files = []

        # Default to TXT if no formats specified (backward compatibility)
        if not export_formats:
            export_formats = ["txt"]

        # Generate structure file
        if all_files:
            if callback:
                callback("Generating structure tree...", 0.1)

            tree = self.tree_builder.build_tree(
                self.project_path, ignored_items, all_files
            )

            with open(self.structure_file, "w", encoding="utf-8") as f:
                f.write(f"# {self.project_path.name} | Structure | {timestamp}\n\n")
                f.write(tree)
            generated_files.append(str(self.structure_file.name))

        # Generate config output files in each format
        total_configs = len(categorized_files)
        total_formats = len(export_formats)
        total_stats = {"total_chars": 0, "total_files_included": 0}

        config_idx = 0
        for config_name, text_files in categorized_files.items():
            if not text_files:
                continue

            config_idx += 1

            for fmt_idx, fmt in enumerate(export_formats):
                if cancel_event and cancel_event.is_set():
                    return False, "Cancelled", {}

                if fmt not in FORMATTERS:
                    continue

                formatter = FORMATTERS[fmt]()
                extension = formatter.get_extension()
                output_filename = f"{config_name}.{extension}"
                output_path = self.output_dir / output_filename

                # Calculate progress
                progress = (
                    0.2
                    + (
                        (config_idx - 1) / total_configs
                        + fmt_idx / (total_configs * total_formats)
                    )
                    * 0.8
                )

                if callback:
                    callback(
                        f"Generating {output_filename} ({len(text_files)} files)...",
                        progress,
                    )

                try:
                    content = formatter.format_output(
                        config_name, timestamp, text_files
                    )

                    with open(output_path, "w", encoding="utf-8") as outfile:
                        outfile.write(content)

                    generated_files.append(output_filename)
                    total_stats["total_chars"] += len(content)

                except Exception as e:
                    print(f"Error creating {output_filename}: {e}")

            total_stats["total_files_included"] += len(text_files)

        stats = {
            "generated_files": generated_files,
            "output_dir": str(self.output_dir),
            "structure_file": str(self.structure_file),
            "total_chars": total_stats["total_chars"],
            "total_files_included": total_stats["total_files_included"],
            "ignored_items": len(ignored_items),
            "summary": f"Created {len(generated_files)} files with {total_stats['total_files_included']} source files.",
        }

        return True, "Process Complete", stats
