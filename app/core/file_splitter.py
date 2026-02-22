"""File splitter module for splitting large output files into smaller parts.

Splits output files at file boundaries (never mid-file) to ensure
each part is self-contained and readable by AI tools with size limits.
"""

import os
from pathlib import Path
from app.core.token_counter import estimate_tokens


def split_output_file(
    output_path: str,
    split_count: int = 5,
) -> list[str]:
    """Split a generated output file into smaller numbered parts.

    Splits at file boundaries (// path markers) to keep files intact.

    Args:
        output_path: Path to the output file to split.
        split_count: Number of parts to split into.

    Returns:
        List of generated split file paths (empty if no split needed).
    """
    if not os.path.exists(output_path):
        return []

    with open(output_path, "r", encoding="utf-8") as f:
        full_content = f.read()

    # Parse the file into header + individual file blocks
    header, file_blocks = _parse_file_blocks(full_content)

    if not file_blocks:
        return []

    # Distribute file blocks evenly across split_count parts
    parts = _distribute_blocks(file_blocks, split_count)

    # Write each part to a numbered file
    base_path = Path(output_path)
    stem = base_path.stem
    ext = base_path.suffix
    parent = base_path.parent

    generated_files = []
    total_parts = len(parts)

    for i, part_blocks in enumerate(parts, start=1):
        part_filename = f"{stem}_{i}{ext}"
        part_path = parent / part_filename

        part_header = (
            f"{header.rstrip()}\n"
            f"# Part {i}/{total_parts}\n\n"
        )
        part_content = part_header + "\n".join(part_blocks)

        with open(part_path, "w", encoding="utf-8") as f:
            f.write(part_content)

        generated_files.append(str(part_path))

    return generated_files


def _parse_file_blocks(content: str) -> tuple[str, list[str]]:
    """Parse output content into header and individual file blocks.

    Detects file boundaries using '// path' markers used by TXT formatter.

    Args:
        content: Full file content.

    Returns:
        Tuple of (header_text, list_of_file_blocks).
    """
    lines = content.split("\n")
    header_lines = []
    blocks = []
    current_block_lines = []
    in_header = True

    for line in lines:
        # Detect file boundary: lines starting with "// " followed by a path
        if line.startswith("// ") and _looks_like_file_path(line[3:]):
            if in_header:
                in_header = False

            # Save previous block if exists
            if current_block_lines:
                blocks.append("\n".join(current_block_lines))

            current_block_lines = [line]
        else:
            if in_header:
                header_lines.append(line)
            else:
                current_block_lines.append(line)

    # Save last block
    if current_block_lines:
        blocks.append("\n".join(current_block_lines))

    header = "\n".join(header_lines)
    return header, blocks


def _looks_like_file_path(text: str) -> bool:
    """Heuristic check if text looks like a file path.

    Args:
        text: Text after '// ' marker.

    Returns:
        True if the text looks like a relative file path.
    """
    text = text.strip()
    if not text:
        return False
    # File paths typically contain / or \ and have an extension
    has_separator = "/" in text or "\\" in text
    has_extension = "." in text.split("/")[-1].split("\\")[-1]
    # Avoid matching regular comments that happen to start with //
    no_spaces_in_path = " " not in text or text.count("/") > 0
    return (has_separator or has_extension) and no_spaces_in_path


def _chunk_large_block(block: str, max_tokens: int) -> list[str]:
    """Split a single file block that exceeds max_tokens into smaller chunks.

    Splits by lines and injects a part suffix into the file header comment
    so AI context is preserved, e.g. ``// src/app.py (Part 1/3)``.

    Args:
        block: A single file block starting with a ``// path`` marker.
        max_tokens: Maximum tokens allowed per chunk.

    Returns:
        List of chunked blocks. Returns the original block unchanged when
        the block fits within max_tokens or has no parseable header.
    """
    if estimate_tokens(block) <= max_tokens:
        return [block]

    lines = block.split("\n")
    if not lines:
        return [block]

    header_line = lines[0]      # e.g. "// src/foo.py"
    content_lines = lines[1:]   # everything after the path marker

    # Accumulate lines into chunks, keeping each chunk under max_tokens
    chunks: list[list[str]] = []
    current: list[str] = []
    # Reserve tokens for the header that will be prepended to each chunk
    reserved = estimate_tokens(header_line) + 10

    for line in content_lines:
        line_tokens = estimate_tokens(line)
        current_tokens = estimate_tokens("\n".join(current)) if current else 0
        if current and current_tokens + line_tokens + reserved > max_tokens:
            chunks.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        chunks.append(current)

    # No real split happened (only 1 chunk) — return as-is
    if len(chunks) <= 1:
        return [block]

    total = len(chunks)
    result = []
    for i, chunk_lines in enumerate(chunks, start=1):
        chunk_header = f"{header_line} (Part {i}/{total})"
        result.append(chunk_header + "\n" + "\n".join(chunk_lines))

    return result


def _distribute_blocks(blocks: list[str], split_count: int) -> list[list[str]]:
    """Distribute file blocks across parts using sequential distribution.

    Preserves the original track order (highest-priority files always land
    in codebase_1, next batch in codebase_2, etc.).  Files whose token count
    exceeds ``target_per_part`` are pre-split by :func:`_chunk_large_block`
    so no single file is left unsplit.

    Algorithm
    ---------
    1. Compute ``target_per_part = total_tokens / split_count``.
    2. Pre-process: any block larger than ``target_per_part`` is expanded
       into smaller line-based chunks (preserving header context).
    3. Walk through the (possibly expanded) block list sequentially.
       When the running token total of the current part would exceed the
       target **and** there are still remaining parts to fill, advance to
       the next part.

    Args:
        blocks: List of file content blocks **in track order**.
        split_count: Target number of output parts.

    Returns:
        List of lists, each containing blocks for one part.
    """
    if not blocks:
        return []

    # Step 1 – measure tokens for every incoming block
    raw_token_pairs = [(b, estimate_tokens(b)) for b in blocks]
    total_tokens = sum(t for _, t in raw_token_pairs)
    target_per_part = max(1, total_tokens // max(1, split_count))

    # Step 2 – pre-split any block that alone exceeds the target
    processed: list[str] = []
    for block, tokens in raw_token_pairs:
        if tokens > target_per_part:
            processed.extend(_chunk_large_block(block, target_per_part))
        else:
            processed.append(block)

    # Step 3 – sequential distribution (preserves order)
    parts: list[list[str]] = [[]]
    current_tokens = 0
    current_part_idx = 0
    max_part_idx = split_count - 1

    for block in processed:
        tokens = estimate_tokens(block)
        # Advance to next part when budget is exhausted (but never exceed split_count)
        if current_tokens > 0 and current_tokens + tokens > target_per_part and current_part_idx < max_part_idx:
            parts.append([])
            current_part_idx += 1
            current_tokens = 0

        parts[current_part_idx].append(block)
        current_tokens += tokens

    return [p for p in parts if p]
