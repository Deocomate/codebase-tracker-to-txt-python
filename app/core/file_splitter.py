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
    current_tokens = 0

    for line in content_lines:
        line_tokens = estimate_tokens(line)
        # +1 accounts for the newline separator between lines
        added_tokens = line_tokens + (1 if current else 0)
        if current and current_tokens + added_tokens + reserved > max_tokens:
            chunks.append(current)
            current = [line]
            current_tokens = line_tokens
        else:
            current.append(line)
            current_tokens += added_tokens

    if current:
        chunks.append(current)

    # Fallback: if line-level split produced only 1 chunk (e.g. a single
    # massive line like minified JS), split on character boundaries instead.
    if len(chunks) <= 1:
        from app.core.token_counter import CHARS_PER_TOKEN
        full_content = "\n".join(content_lines)
        chars_per_chunk = max(1, (max_tokens - reserved) * CHARS_PER_TOKEN)
        if len(full_content) > chars_per_chunk:
            char_chunks = [
                full_content[i:i + chars_per_chunk]
                for i in range(0, len(full_content), chars_per_chunk)
            ]
            total = len(char_chunks)
            result = []
            for i, chunk_text in enumerate(char_chunks, start=1):
                chunk_header = f"{header_line} (Part {i}/{total})"
                result.append(chunk_header + "\n" + chunk_text)
            return result
        return [block]

    total = len(chunks)
    result = []
    for i, chunk_lines in enumerate(chunks, start=1):
        chunk_header = f"{header_line} (Part {i}/{total})"
        result.append(chunk_header + "\n" + "\n".join(chunk_lines))

    return result


def _distribute_blocks(blocks: list[str], split_count: int) -> list[list[str]]:
    """Distribute file blocks across parts using LPT bin-packing.

    Uses the Longest Processing Time (LPT) heuristic to achieve
    near-optimal token balance across parts.  Each block is assigned
    to the part with the fewest accumulated tokens.  Original file
    order is preserved within each part.

    Algorithm
    ---------
    1. Compute ``target_per_part = total_tokens / split_count``.
    2. Pre-process: any block larger than ``target_per_part`` is expanded
       into smaller line-based chunks (preserving header context).
    3. Tag every (possibly expanded) block with its original index.
    4. Sort blocks by token count **descending** (largest first).
    5. Assign each block to the bin (part) with the smallest current
       token total.
    6. Sort blocks inside each bin by original index to restore
       the natural file order within that part.

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
    processed: list[tuple[int, str]] = []  # (original_index, block)
    orig_idx = 0
    for block, tokens in raw_token_pairs:
        if tokens > target_per_part:
            for chunk in _chunk_large_block(block, target_per_part):
                processed.append((orig_idx, chunk))
        else:
            processed.append((orig_idx, block))
        orig_idx += 1

    # Step 3 – compute tokens for processed blocks
    indexed_blocks = [
        (idx, blk, estimate_tokens(blk)) for idx, blk in processed
    ]

    # Step 4 – sort by token count descending (LPT: largest first)
    sorted_blocks = sorted(indexed_blocks, key=lambda x: x[2], reverse=True)

    # Step 5 – assign each block to the least-loaded bin
    actual_parts = min(split_count, len(sorted_blocks))
    bins: list[list[tuple[int, str]]] = [[] for _ in range(actual_parts)]
    bin_tokens: list[int] = [0] * actual_parts

    for orig_idx, blk, tokens in sorted_blocks:
        # Find the bin with the smallest current total
        min_bin = min(range(actual_parts), key=lambda i: bin_tokens[i])
        bins[min_bin].append((orig_idx, blk))
        bin_tokens[min_bin] += tokens

    # Step 6 – restore original file order within each bin
    # and sort parts by their earliest original index
    part_with_min_idx: list[tuple[int, list[str]]] = []
    for bin_items in bins:
        if bin_items:
            bin_items.sort(key=lambda x: x[0])
            min_idx = bin_items[0][0]
            part_with_min_idx.append(
                (min_idx, [blk for _, blk in bin_items])
            )

    # Sort parts so part 1 starts with the earliest original files
    part_with_min_idx.sort(key=lambda x: x[0])

    return [blocks for _, blocks in part_with_min_idx]
