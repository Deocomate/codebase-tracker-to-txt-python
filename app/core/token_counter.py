"""Token counter using Gemini-standard estimation.

Gemini uses SentencePiece BPE tokenizer. For code content,
the standard approximation is ~4 characters per token.
This module provides token estimation without requiring external API calls.
"""

# Gemini tokenizer averages ~4 characters per token for code/mixed content
CHARS_PER_TOKEN = 4

# Default threshold: split only when tokens exceed this value
DEFAULT_TOKEN_THRESHOLD = 40_000


def estimate_tokens(text: str) -> int:
    """Estimate token count using Gemini's ~4 chars/token ratio.

    Args:
        text: The text content to estimate tokens for.

    Returns:
        Estimated number of tokens.
    """
    if not text:
        return 0
    return max(1, len(text) // CHARS_PER_TOKEN)


def should_split(text: str, threshold: int = DEFAULT_TOKEN_THRESHOLD) -> bool:
    """Check if content exceeds the token threshold and needs splitting.

    Args:
        text: The text content to check.
        threshold: Maximum tokens before splitting is triggered.

    Returns:
        True if the content should be split.
    """
    return estimate_tokens(text) > threshold
