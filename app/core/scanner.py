import os
import pathspec
from pathlib import Path
from app.core.ignore_rules import IgnoreRules
from app.utils.file_utils import is_text_file, get_relative_path

class FileScanner:
    def __init__(self, project_path):
        self.project_path = Path(project_path).absolute()
        self.ignore_rules = IgnoreRules(self.project_path)

    def _sort_files_by_pattern_order(self, files, config_name):
        """
        Reorder files based on the order of patterns in the 'tracks' config.
        Files matching earlier patterns appear first.
        """
        # Find the config dictionary for this config_name
        config = next((c for c in self.ignore_rules.settings.get("track_config", []) 
                       if c.get("name") == config_name), None)
        
        if not config or "tracks" not in config:
            # Fallback to default sorting (alphabetical by relative path)
            return sorted(files, key=lambda x: x[1])

        patterns = config["tracks"]
        
        # Optimization: If only "*" is present, just sort alphabetically
        if len(patterns) == 1 and patterns[0] == "*":
            return sorted(files, key=lambda x: x[1])

        ordered_files = []
        remaining_files = files[:] # Copy of the list to manipulate

        # Iterate through patterns in the order defined by user
        for pattern in patterns:
            # Create a matcher for this specific pattern
            spec = pathspec.PathSpec.from_lines('gitwildmatch', [pattern])
            
            matches = []
            non_matches = []

            for file_tuple in remaining_files:
                # file_tuple is (abs_path, rel_path)
                # Ensure path is POSIX style for matching
                rel_path_str = file_tuple[1].replace(os.sep, '/')
                
                if spec.match_file(rel_path_str):
                    matches.append(file_tuple)
                else:
                    non_matches.append(file_tuple)
            
            # Sort matches alphabetically within this specific pattern group
            # This ensures stability: User defined order > Alphabetical order
            matches.sort(key=lambda x: x[1])
            
            ordered_files.extend(matches)
            remaining_files = non_matches # Only process non-matched files for next patterns

        # If any files remain (matched by general rules but missed by specific sort logic somehow), 
        # append them at the end sorted alphabetically.
        if remaining_files:
            remaining_files.sort(key=lambda x: x[1])
            ordered_files.extend(remaining_files)

        return ordered_files

    def scan(self, callback=None, cancel_event=None):
        """Scan project and categorize files by config."""
        categorized_files = {name: [] for name in self.ignore_rules.configs.keys()}
        ignored_items = []
        all_files_for_tree = []

        if callback:
            callback("Discovering and categorizing files...", -1)

        for root, dirs, files in os.walk(self.project_path, topdown=True):
            if cancel_event and cancel_event.is_set():
                break

            root_path = Path(root)
            rel_root = get_relative_path(root_path, self.project_path)
            if rel_root == '.':
                rel_root = ''

            # Filter directories
            dirs_to_keep = []
            for d in dirs:
                dir_abs_path = root_path / d
                dir_rel_path = os.path.join(rel_root, d) if rel_root else d
                
                if self.ignore_rules.is_globally_ignored(dir_rel_path, is_dir=True):
                    ignored_items.append((dir_abs_path, dir_rel_path, "global_ignore"))
                else:
                    dirs_to_keep.append(d)
            dirs[:] = dirs_to_keep

            if rel_root:
                all_files_for_tree.append(rel_root)

            for d in dirs:
                all_files_for_tree.append(get_relative_path(root_path / d, self.project_path))

            # Process files
            for filename in files:
                if cancel_event and cancel_event.is_set():
                    break

                file_path = root_path / filename
                rel_path = get_relative_path(file_path, self.project_path)
                all_files_for_tree.append(rel_path)

                if self.ignore_rules.is_globally_ignored(rel_path, is_dir=False):
                    ignored_items.append((file_path, rel_path, "global_ignore"))
                    continue

                matching_configs = self.ignore_rules.get_matching_configs(rel_path)
                if not matching_configs:
                    ignored_items.append((file_path, rel_path, "no_track_match"))
                    continue

                if is_text_file(file_path):
                    for config_name in matching_configs:
                        categorized_files[config_name].append((file_path, rel_path))
                else:
                    ignored_items.append((file_path, rel_path, "binary"))

        if cancel_event and cancel_event.is_set():
            if callback:
                callback("Scan cancelled by user.", -1)
            return {}, [], []

        # OPTIMIZATION: Sort files based on 'tracks' order in settings
        if callback:
            callback("Ordering files...", -1)
            
        for config_name in categorized_files:
            categorized_files[config_name] = self._sort_files_by_pattern_order(
                categorized_files[config_name], 
                config_name
            )

        if callback:
            total_matches = sum(len(v) for v in categorized_files.values())
            callback(f"Scan complete! Found {total_matches} matches for {len(categorized_files)} configurations.", -1)

        return categorized_files, ignored_items, all_files_for_tree
