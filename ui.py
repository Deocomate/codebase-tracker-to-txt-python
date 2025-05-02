# Đây là phiên bản rút gọn của ui.py, chỉ hiển thị phần thay đổi
# Cần thay đổi phương thức _process_project() như sau

def _process_project(self):
    """Process the project (scan and combine) in a background thread"""
    try:
        # Scan files
        self._update_status("Scanning project files...", 0.1)
        text_files, binary_files, ignored_items, all_files = self.scanner.scan(callback=self._scan_callback)

        self._log(f"Scan complete!")
        self._log(f"Found {len(text_files)} text files and {len(binary_files)} binary files")
        self._log(f"Ignored {len(ignored_items)} items based on ignore rules")

        # Combine files
        self._update_status("Combining files...", 0.5)
        success, message, stats = self.combiner.combine(
            text_files,
            binary_files,
            ignored_items,
            self.scanner.ignore_rules,
            all_files,
            callback=self._combine_callback
        )

        if success:
            self._update_status(f"Success! {message}", 1.0)
            self._log(f"Combined {stats['text_files']} text files into {stats['output_file']}")
            self._log(f"Total characters in output: {stats['total_chars']:,}")

            # Show results frame
            self.root.after(0, self._show_results, stats)
        else:
            self._update_status(f"Error: {message}", 1.0)
            self._log(f"Failed to combine files: {message}")

    except Exception as e:
        self._update_status(f"Error: {str(e)}", 1.0)
        self._log(f"Exception occurred: {str(e)}")
