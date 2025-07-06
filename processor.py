import threading
from scanner import FileScanner
from combiner import FileCombiner


class ProjectProcessor:
    """
    Acts as a controller/facade to orchestrate the scanning and combining process.
    This decouples the business logic from the UI.
    """
    def __init__(self, project_path):
        self.project_path = project_path
        self.scanner = FileScanner(project_path)
        self.combiner = FileCombiner(project_path)

    def run(self, scan_callback, combine_callback, cancel_event: threading.Event):
        """
        Runs the full scan and combine process.
        Accepts callbacks for UI updates and a cancel_event for interruption.
        Returns (was_successful, message, stats)
        """
        try:
            # --- Scanning phase ---
            scan_callback("Scanning project files...", 0)
            text_files, ignored_items, all_files = self.scanner.scan(
                callback=scan_callback,
                cancel_event=cancel_event
            )

            if cancel_event.is_set():
                return False, "Process was cancelled by user.", {}

            scan_callback(f"Scan complete! Found {len(text_files)} text files.", 0.5)

            # --- Combining phase ---
            combine_callback("Combining files...", 0.5)
            success, message, stats = self.combiner.combine(
                text_files, ignored_items,
                self.scanner.ignore_rules, all_files,
                callback=combine_callback,
                cancel_event=cancel_event
            )

            if cancel_event.is_set():
                return False, "Process was cancelled by user.", {}

            return success, message, stats

        except Exception as e:
            return False, f"An unexpected error occurred: {str(e)}", {}