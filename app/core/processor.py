import threading
from app.core.scanner import FileScanner
from app.core.combiner import FileCombiner


class ProjectProcessor:
    def __init__(self, project_path):
        self.project_path = project_path
        self.scanner = FileScanner(project_path)
        self.combiner = FileCombiner(project_path)

    def run(
        self,
        scan_callback,
        combine_callback,
        cancel_event: threading.Event,
        export_formats=None,
    ):
        """Run the full scan and combine process."""
        try:
            scan_callback("Scanning project files...", 0)
            categorized_files, ignored_items, all_files = self.scanner.scan(
                callback=scan_callback, cancel_event=cancel_event
            )

            if cancel_event.is_set():
                return False, "Process was cancelled by user.", {}

            total_matches = sum(len(v) for v in categorized_files.values())
            scan_callback(
                f"Scan complete! Found {total_matches} matches across {len(categorized_files)} configs.",
                0.5,
            )

            combine_callback("Combining files...", 0.5)
            success, message, stats = self.combiner.combine(
                categorized_files,
                ignored_items,
                self.scanner.ignore_rules,
                all_files,
                callback=combine_callback,
                cancel_event=cancel_event,
                export_formats=export_formats,
            )

            if cancel_event.is_set():
                return False, "Process was cancelled by user.", {}

            return success, message, stats

        except Exception as e:
            return False, f"An unexpected error occurred: {str(e)}", {}
