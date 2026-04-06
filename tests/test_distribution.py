"""Test script for balanced token distribution in file_splitter."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.file_splitter import _distribute_blocks, _chunk_large_block
from app.core.token_counter import estimate_tokens


def make_block(rel_path: str, char_count: int) -> str:
    """Create a mock file block with exact character count."""
    header = f"// {rel_path}"
    # Fill with repeating content to reach target char count
    body_needed = max(0, char_count - len(header) - 1)  # -1 for newline
    body = "x" * body_needed
    return f"{header}\n{body}"


def test_balanced_distribution():
    """Test that LPT bin-packing produces balanced parts."""
    print("=" * 60)
    print("TEST: Balanced distribution across 5 parts")
    print("=" * 60)

    # Simulate a real project: many small files + some large files
    blocks = []
    # 3 large files (~50k tokens each = ~200k chars)
    for i in range(3):
        blocks.append(make_block(f"src/large_{i}.py", 200_000))
    # 20 medium files (~5k tokens each = ~20k chars)
    for i in range(20):
        blocks.append(make_block(f"src/module/medium_{i}.ts", 20_000))
    # 50 small files (~500 tokens each = ~2k chars)
    for i in range(50):
        blocks.append(make_block(f"src/utils/small_{i}.ts", 2_000))

    split_count = 5

    total_tokens = sum(estimate_tokens(b) for b in blocks)
    print(f"\nTotal blocks: {len(blocks)}")
    print(f"Total tokens: {total_tokens:,}")
    print(f"Ideal per part: {total_tokens // split_count:,}")

    parts = _distribute_blocks(blocks, split_count)

    print(f"\nDistribution ({len(parts)} parts):")
    part_tokens = []
    for i, part in enumerate(parts, 1):
        tokens = sum(estimate_tokens(b) for b in part)
        part_tokens.append(tokens)
        print(f"  Part {i}: {tokens:>8,} tokens ({len(part):>3} blocks)")

    max_t = max(part_tokens)
    min_t = min(part_tokens)
    ratio = max_t / min_t if min_t > 0 else float('inf')
    print(f"\n  Max/Min ratio: {ratio:.2f}x")
    print(f"  Max: {max_t:,}  Min: {min_t:,}")

    # Assert balance: max/min ratio should be <= 1.5x
    assert ratio <= 1.5, f"FAIL: ratio {ratio:.2f}x exceeds 1.5x threshold"
    print("  ✅ PASS: ratio <= 1.5x")

    # Assert total preserved
    distributed_total = sum(part_tokens)
    assert distributed_total == total_tokens, \
        f"FAIL: total changed ({distributed_total} vs {total_tokens})"
    print("  ✅ PASS: total tokens preserved")


def test_single_huge_file():
    """Test that a single huge file gets pre-split correctly."""
    print("\n" + "=" * 60)
    print("TEST: Single huge file (200k tokens)")
    print("=" * 60)

    blocks = [make_block("src/giant.py", 800_000)]  # ~200k tokens
    split_count = 5

    parts = _distribute_blocks(blocks, split_count)

    part_tokens = []
    for i, part in enumerate(parts, 1):
        tokens = sum(estimate_tokens(b) for b in part)
        part_tokens.append(tokens)
        print(f"  Part {i}: {tokens:>8,} tokens ({len(part):>3} blocks)")

    max_t = max(part_tokens)
    min_t = min(part_tokens)
    ratio = max_t / min_t if min_t > 0 else float('inf')
    print(f"\n  Max/Min ratio: {ratio:.2f}x")
    assert ratio <= 1.5, f"FAIL: ratio {ratio:.2f}x exceeds 1.5x"
    print("  ✅ PASS")


def test_extreme_skew():
    """Test with extreme size differences: 1 giant + 100 tiny files."""
    print("\n" + "=" * 60)
    print("TEST: Extreme skew (1x200k + 100x500 tokens)")
    print("=" * 60)

    blocks = [make_block("src/monster.py", 800_000)]
    for i in range(100):
        blocks.append(make_block(f"src/tiny_{i}.ts", 2_000))

    split_count = 5
    total_tokens = sum(estimate_tokens(b) for b in blocks)

    parts = _distribute_blocks(blocks, split_count)

    part_tokens = []
    for i, part in enumerate(parts, 1):
        tokens = sum(estimate_tokens(b) for b in part)
        part_tokens.append(tokens)
        print(f"  Part {i}: {tokens:>8,} tokens ({len(part):>3} blocks)")

    max_t = max(part_tokens)
    min_t = min(part_tokens)
    ratio = max_t / min_t if min_t > 0 else float('inf')
    print(f"\n  Max/Min ratio: {ratio:.2f}x")
    assert ratio <= 2.0, f"FAIL: ratio {ratio:.2f}x exceeds 2.0x"
    print("  ✅ PASS: ratio <= 2.0x")


def test_chunk_large_block_performance():
    """Test _chunk_large_block with a large block doesn't take too long."""
    print("\n" + "=" * 60)
    print("TEST: _chunk_large_block performance")
    print("=" * 60)

    import time
    # 500k chars = ~125k tokens, split into 25k token chunks
    block = make_block("src/huge.py", 500_000)
    max_tokens = 25_000

    start = time.perf_counter()
    chunks = _chunk_large_block(block, max_tokens)
    elapsed = time.perf_counter() - start

    print(f"  Block: {estimate_tokens(block):,} tokens")
    print(f"  Split into {len(chunks)} chunks in {elapsed:.3f}s")
    for i, c in enumerate(chunks, 1):
        print(f"    Chunk {i}: {estimate_tokens(c):,} tokens")

    assert elapsed < 1.0, f"FAIL: took {elapsed:.3f}s (>1s)"
    print(f"  ✅ PASS: completed in {elapsed:.3f}s")


if __name__ == "__main__":
    test_balanced_distribution()
    test_single_huge_file()
    test_extreme_skew()
    test_chunk_large_block_performance()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
