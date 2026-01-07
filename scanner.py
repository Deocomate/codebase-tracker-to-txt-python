import os
from pathlib import Path
from ignore_rules import IgnoreRules
from file_utils import is_text_file, get_relative_path


class FileScanner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.ignore_rules = IgnoreRules(self.project_path)

    def scan(self, callback=None, cancel_event=None):
        # Data structure: { "config_name": [ (file_path, rel_path), ... ] }
        categorized_files = {name: [] for name in self.ignore_rules.configs.keys()}
        
        # To verify global ignores for statistics
        ignored_items = [] 
        all_files_for_tree = []

        if callback: callback("Discovering and categorizing files...", -1)

        for root, dirs, files in os.walk(self.project_path, topdown=True):
            if cancel_event and cancel_event.is_set(): break
            
            root_path = Path(root)
            rel_root = get_relative_path(root_path, self.project_path)
            if rel_root == '.': rel_root = ''

            # Filter directories based on GLOBAL ignore rules only to speed up walk
            # Note: We don't filter by specific config ignores here, as one dir might be ignored in A but not B
            dirs[:] = [d for d in dirs if not self.ignore_rules.is_globally_ignored(os.path.join(rel_root, d))]
            
            # Record structure
            if rel_root:
                all_files_for_tree.append(rel_root)
            for d in dirs:
                all_files_for_tree.append(get_relative_path(root_path / d, self.project_path))

            for filename in files:
                if cancel_event and cancel_event.is_set(): break
                
                file_path = root_path / filename
                rel_path = get_relative_path(file_path, self.project_path)
                all_files_for_tree.append(rel_path)

                # 1. Check Global Ignore
                if self.ignore_rules.is_globally_ignored(rel_path):
                    ignored_items.append((file_path, rel_path, "global_ignore"))
                    continue

                # 2. Check which configs match this file
                matching_configs = self.ignore_rules.get_matching_configs(rel_path)
                
                if not matching_configs:
                    ignored_items.append((file_path, rel_path, "no_track_match"))
                    continue

                # 3. Check if text file
                if is_text_file(file_path):
                    for config_name in matching_configs:
                        categorized_files[config_name].append((file_path, rel_path))
                else:
                    ignored_items.append((file_path, rel_path, "binary"))

        if cancel_event and cancel_event.is_set():
            if callback: callback("Scan cancelled by user.", -1)
            return {}, [], []

        total_files_found = sum(len(files) for files in categorized_files.values())
        if callback:
            callback(f"Scan complete! Found matches for {len(categorized_files)} configurations.", -1)
            
        return categorized_files, ignored_items, all_files_for_tree