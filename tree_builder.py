from pathlib import Path
import os


class TreeBuilder:
    """Build a tree representation of project structure"""

    def __init__(self):
        self.indent_symbol = "    "  # 4 spaces
        self.branch_symbol = "│   "
        self.tee_symbol = "├── "
        self.last_symbol = "└── "

    def build_tree(self, project_path, ignored_dirs, all_files, max_depth=None):
        """
        Build a tree representation of the project structure.

        Args:
            project_path: Root path of the project
            ignored_dirs: Set of directory paths that are ignored
            all_files: List of all files (both included and ignored)
            max_depth: Maximum depth to display (None for unlimited)

        Returns:
            String representation of the tree structure
        """
        project_path = Path(project_path).absolute()
        root_name = project_path.name

        # Start with the root
        tree_lines = ["."]

        # Build file structure map
        file_structure = {}
        ignored_dirs_set = set()

        # Convert ignored_dirs to a set of normalized paths
        for dir_path in ignored_dirs:
            # Ensure path is relative to project root
            if isinstance(dir_path, tuple) and len(dir_path) > 1:
                rel_path = dir_path[1]
            else:
                rel_path = str(dir_path)

            ignored_dirs_set.add(self._normalize_path(rel_path))

        # Add all files to the structure
        for file_item in all_files:
            # Handle different formats of file items
            if isinstance(file_item, tuple) and len(file_item) >= 2:
                # From ignored_items or text_files/binary_files list
                abs_path, rel_path = file_item[0], file_item[1]
                is_dir = os.path.isdir(abs_path) if abs_path else False
            else:
                # Direct path object
                rel_path = file_item
                is_dir = os.path.isdir(os.path.join(project_path, rel_path))

            # Skip .codebase directory
            if str(rel_path).startswith('.codebase'):
                continue

            # Create path components
            path_parts = self._normalize_path(rel_path).split('/')

            # Build the structure
            current_dict = file_structure
            current_path = ""

            for i, part in enumerate(path_parts):
                if not part:  # Skip empty parts
                    continue

                # Build the current path for ignore checking
                if current_path:
                    current_path += f"/{part}"
                else:
                    current_path = part

                # Check if this path or any parent is ignored
                path_ignored = current_path in ignored_dirs_set or any(
                    current_path.startswith(ignored_dir + '/')
                    for ignored_dir in ignored_dirs_set
                )

                # If it's the last part (file name)
                if i == len(path_parts) - 1:
                    # If it's a directory or the final component
                    if is_dir or i == len(path_parts) - 1:
                        if part not in current_dict:
                            current_dict[part] = {"__is_dir__": is_dir, "__ignored__": path_ignored}
                else:
                    # It's a directory component
                    if part not in current_dict:
                        current_dict[part] = {"__is_dir__": True, "__ignored__": path_ignored}
                    elif "__is_dir__" not in current_dict[part]:
                        current_dict[part]["__is_dir__"] = True

                    # Only descend into non-ignored directories
                    if not current_dict[part].get("__ignored__"):
                        current_dict = current_dict[part]

        # Recursively build the tree lines
        self._build_tree_recursive(file_structure, tree_lines, "", 0, max_depth)

        return "\n".join(tree_lines)

    def _build_tree_recursive(self, node, lines, prefix, depth, max_depth):
        """
        Recursively build tree lines.

        Args:
            node: Current node in the file structure
            lines: List of lines to append to
            prefix: Current line prefix for indentation
            depth: Current depth in the tree
            max_depth: Maximum depth to display
        """
        if max_depth is not None and depth > max_depth:
            return

        # Get all entries except metadata
        entries = [(k, v) for k, v in node.items() if not k.startswith("__")]
        entries.sort(key=lambda x: (not x[1].get("__is_dir__", False), x[0].lower()))

        # Process each entry
        for i, (name, contents) in enumerate(entries):
            is_last = i == len(entries) - 1
            is_dir = contents.get("__is_dir__", False)
            is_ignored = contents.get("__ignored__", False)

            # Add this item
            if is_last:
                lines.append(f"{prefix}{self.last_symbol}{name}{'/' if is_dir else ''}")
                new_prefix = prefix + self.indent_symbol
            else:
                lines.append(f"{prefix}{self.tee_symbol}{name}{'/' if is_dir else ''}")
                new_prefix = prefix + self.branch_symbol

            # If directory and not ignored, add its children
            if is_dir and not is_ignored:
                # Only recurse into non-ignored directories with contents
                filtered_contents = {k: v for k, v in contents.items() if not k.startswith("__")}
                if filtered_contents:
                    self._build_tree_recursive(contents, lines, new_prefix, depth + 1, max_depth)

    def _normalize_path(self, path):
        """Normalize path for consistent processing"""
        if isinstance(path, Path):
            path = str(path)

        # Convert backslashes to forward slashes
        path = path.replace('\\', '/')

        # Remove leading and trailing slashes
        path = path.strip('/')

        return path