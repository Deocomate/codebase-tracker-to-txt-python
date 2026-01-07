from pathlib import Path
import os


class TreeBuilder:
    """Build a tree representation of project structure."""

    def __init__(self):
        self.indent_symbol = "    "
        self.branch_symbol = "│   "
        self.tee_symbol = "├── "
        self.last_symbol = "└── "

    def build_tree(self, project_path, ignored_dirs, all_files, max_depth=None):
        """Build a tree representation of the project structure."""
        project_path = Path(project_path).absolute()
        tree_lines = ["."]
        file_structure = {}
        ignored_dirs_set = set()

        for dir_path in ignored_dirs:
            if isinstance(dir_path, tuple) and len(dir_path) > 1:
                rel_path = dir_path[1]
            else:
                rel_path = str(dir_path)
            ignored_dirs_set.add(self._normalize_path(rel_path))

        for file_item in all_files:
            if isinstance(file_item, tuple) and len(file_item) >= 2:
                abs_path, rel_path = file_item[0], file_item[1]
                is_dir = os.path.isdir(abs_path) if abs_path else False
            else:
                rel_path = file_item
                is_dir = os.path.isdir(os.path.join(project_path, rel_path))

            if str(rel_path).startswith('_codebase'):
                continue

            path_parts = self._normalize_path(rel_path).split('/')
            current_dict = file_structure
            current_path = ""

            for i, part in enumerate(path_parts):
                if not part:
                    continue

                current_path = f"{current_path}/{part}" if current_path else part
                path_ignored = current_path in ignored_dirs_set or any(
                    current_path.startswith(d + '/') for d in ignored_dirs_set
                )

                if i == len(path_parts) - 1:
                    if is_dir or i == len(path_parts) - 1:
                        if part not in current_dict:
                            current_dict[part] = {"__is_dir__": is_dir, "__ignored__": path_ignored}
                else:
                    if part not in current_dict:
                        current_dict[part] = {"__is_dir__": True, "__ignored__": path_ignored}
                    elif "__is_dir__" not in current_dict[part]:
                        current_dict[part]["__is_dir__"] = True

                    if not current_dict[part].get("__ignored__"):
                        current_dict = current_dict[part]

        self._build_tree_recursive(file_structure, tree_lines, "", 0, max_depth)
        return "\n".join(tree_lines)

    def _build_tree_recursive(self, node, lines, prefix, depth, max_depth):
        """Recursively build tree lines."""
        if max_depth is not None and depth > max_depth:
            return

        entries = [(k, v) for k, v in node.items() if not k.startswith("__")]
        entries.sort(key=lambda x: (not x[1].get("__is_dir__", False), x[0].lower()))

        for i, (name, contents) in enumerate(entries):
            is_last = i == len(entries) - 1
            is_dir = contents.get("__is_dir__", False)
            is_ignored = contents.get("__ignored__", False)

            if is_last:
                lines.append(f"{prefix}{self.last_symbol}{name}{'/' if is_dir else ''}")
                new_prefix = prefix + self.indent_symbol
            else:
                lines.append(f"{prefix}{self.tee_symbol}{name}{'/' if is_dir else ''}")
                new_prefix = prefix + self.branch_symbol

            if is_dir and not is_ignored:
                filtered = {k: v for k, v in contents.items() if not k.startswith("__")}
                if filtered:
                    self._build_tree_recursive(contents, lines, new_prefix, depth + 1, max_depth)

    def _normalize_path(self, path):
        """Normalize path for consistent processing."""
        if isinstance(path, Path):
            path = str(path)
        return path.replace('\\', '/').strip('/')
