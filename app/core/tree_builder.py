import os
from pathlib import Path


class TreeBuilder:
    """Build a tree representation of project structure."""

    def __init__(self):
        self.indent_symbol = "    "
        self.branch_symbol = "│   "
        self.tee_symbol = "├── "
        self.last_symbol = "└── "

    def _normalize_path(self, path):
        """
        Normalize path to POSIX style (forward slashes) for consistent processing.
        """
        if isinstance(path, Path):
            path = str(path)
        return path.replace(os.sep, '/').strip('/')

    def build_tree(self, project_path, ignored_items, all_files, max_depth=None):
        """
        Build a tree representation of the project structure.
        
        Args:
            project_path: Path to the project root.
            ignored_items: List of ignored items from scanner, each is a tuple (abs_path, rel_path, reason).
            all_files: List of all file/dir paths (relative) discovered during scan.
            max_depth: Optional max depth for the tree.
        
        Returns:
            String representation of the tree.
        """
        project_path = Path(project_path).absolute()
        tree_lines = ["."]
        file_structure = {}
        
        # Build set of ignored paths for quick lookup
        ignored_paths_set = set()
        for item in ignored_items:
            if isinstance(item, tuple) and len(item) >= 2:
                rel_path = self._normalize_path(item[1])
                ignored_paths_set.add(rel_path)

        # Process all files/dirs to build hierarchical structure
        for file_item in all_files:
            # Extract relative path from item (could be string or tuple)
            if isinstance(file_item, tuple) and len(file_item) >= 2:
                rel_path = self._normalize_path(file_item[1])
                abs_path = file_item[0]
                # Determine if directory from the absolute path
                is_dir = Path(abs_path).is_dir() if abs_path and Path(abs_path).exists() else False
            else:
                rel_path = self._normalize_path(file_item)
                abs_path = project_path / rel_path
                is_dir = abs_path.is_dir() if abs_path.exists() else '/' not in rel_path and not Path(rel_path).suffix

            # Skip _codebase folder (internal output folder)
            if rel_path.startswith('_codebase'):
                continue

            # Check if this path or any parent is ignored
            is_ignored = rel_path in ignored_paths_set or any(
                rel_path.startswith(ignored + '/') for ignored in ignored_paths_set
            )

            # Build nested dictionary structure
            path_parts = rel_path.split('/')
            current_dict = file_structure
            current_path = ""

            for i, part in enumerate(path_parts):
                if not part:
                    continue

                current_path = f"{current_path}/{part}" if current_path else part
                is_last_part = (i == len(path_parts) - 1)
                
                # Check if current path is specifically ignored
                path_ignored = current_path in ignored_paths_set

                if part not in current_dict:
                    current_dict[part] = {
                        "__is_dir__": not is_last_part or is_dir,
                        "__ignored__": path_ignored
                    }
                
                # Update ignored status if we found it's ignored
                if path_ignored:
                    current_dict[part]["__ignored__"] = True

                # Navigate deeper only if not the last part and not ignored
                if not is_last_part:
                    if not current_dict[part].get("__ignored__"):
                        current_dict = current_dict[part]
                    else:
                        # Stop building tree for ignored directories
                        break

        self._build_tree_recursive(file_structure, tree_lines, "", 0, max_depth)
        return "\n".join(tree_lines)

    def _build_tree_recursive(self, node, lines, prefix, depth, max_depth):
        """Recursively build tree lines from nested dictionary structure."""
        if max_depth is not None and depth > max_depth:
            return

        # Get entries excluding metadata keys
        entries = [(k, v) for k, v in node.items() if not k.startswith("__")]
        # Sort: directories first, then alphabetically (case-insensitive)
        entries.sort(key=lambda x: (not x[1].get("__is_dir__", False), x[0].lower()))

        for i, (name, contents) in enumerate(entries):
            is_last = i == len(entries) - 1
            is_dir = contents.get("__is_dir__", False)
            is_ignored = contents.get("__ignored__", False)

            # Choose the appropriate prefix symbol
            connector = self.last_symbol if is_last else self.tee_symbol
            
            # Add suffix for directories
            display_name = f"{name}/" if is_dir else name
            
            # Optionally mark ignored items (could add styling later)
            lines.append(f"{prefix}{connector}{display_name}")

            # Choose prefix for children
            new_prefix = prefix + (self.indent_symbol if is_last else self.branch_symbol)

            # Recurse into subdirectories only if not ignored
            if is_dir and not is_ignored:
                # Filter out metadata keys for recursion
                child_entries = {k: v for k, v in contents.items() if not k.startswith("__")}
                if child_entries:
                    self._build_tree_recursive(contents, lines, new_prefix, depth + 1, max_depth)
