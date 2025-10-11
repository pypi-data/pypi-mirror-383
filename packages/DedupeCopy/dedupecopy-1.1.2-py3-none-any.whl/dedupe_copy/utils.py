"""Utility functions for dedupe_copy
"""

import fnmatch
import hashlib
import logging
import os
import sys
import time
from typing import Any, List, Optional, Tuple, Union


logger = logging.getLogger(__name__)

# Optional import of xxhash for faster hashing if available
xxhash: Optional[Any] = None
try:
    import xxhash
except ImportError:
    logger.warning(
        "xxhash module not found. Please install with 'pip install xxhash',"
        " forcing use of 'hash_algo=\"md5\"' in configuration to avoid xxhash."
    )
    xxhash = None

MAX_TARGET_QUEUE_SIZE = 50000
READ_CHUNK = 1048576  # 1 MB


def ensure_logging_configured() -> None:
    """Ensure logging is configured with sensible defaults if not already set"""
    root_logger = logging.getLogger("dedupe_copy")
    if not root_logger.handlers:
        # No handlers configured yet, set up basic configuration
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        root_logger.propagate = False


def format_error_message(path: str, error: Union[str, Exception]) -> str:
    """Format an error message with helpful context and suggestions

    Args:
        path: File path that caused the error
        error: The error or exception that occurred

    Returns:
        Formatted error message with suggestions
    """
    error_str = str(error)
    error_type = type(error).__name__ if isinstance(error, Exception) else "Error"

    # Build helpful message based on error type
    suggestions = []
    if isinstance(error, PermissionError) or "Permission denied" in error_str:
        suggestions.append("Check file permissions")
        suggestions.append("Ensure you have read access to source files")
        suggestions.append("Ensure you have write access to destination")
    elif isinstance(error, FileNotFoundError) or "No such file" in error_str:
        suggestions.append("File may have been deleted during processing")
        suggestions.append("Check if path is on a network share that disconnected")
    elif isinstance(error, OSError) and "Errno 28" in error_str:  # No space left
        suggestions.append("Destination disk is full")
        suggestions.append("Free up space or choose a different destination")
    elif isinstance(error, (IOError, OSError)):
        suggestions.append("Check disk health and connection")
        suggestions.append("For network paths, verify network stability")

    msg = f"Error processing {repr(path)}: [{error_type}] {error_str}"
    if suggestions:
        msg += "\n  Suggestions: " + "; ".join(suggestions)

    return msg


def _throttle_puts(current_size: int) -> None:
    """Delay for some factor to avoid overloading queues"""
    time.sleep(min((current_size * 2) / float(MAX_TARGET_QUEUE_SIZE), 60))


def lower_extension(src: str) -> str:
    """Extract and return the lowercase file extension."""
    _, extension = os.path.splitext(src)
    return extension[1:].lower()


def hash_file(src: str, hash_algo: str = "md5") -> str:
    """Hash a file, returning the checksum hexdigest.

    :param src: Full path of the source file.
    :type src: str
    :param hash_algo: Hashing algorithm to use ('md5' or 'xxh64').
    :type hash_algo: str
    """
    if hash_algo == "xxh64" and not xxhash:
        raise RuntimeError(
            "xxh64 algorithm requested, but the 'xxhash' library is not installed. "
            "Please install it with 'pip install xxhash'."
        )
    if xxhash and hash_algo == "xxh64":
        checksum = xxhash.xxh64()
    else:
        checksum = hashlib.md5()

    with open(src, "rb") as inhandle:
        chunk = inhandle.read(READ_CHUNK)
        while chunk:
            checksum.update(chunk)
            chunk = inhandle.read(READ_CHUNK)
    return checksum.hexdigest()


def read_file(src: str, hash_algo: str = "md5") -> Tuple[str, int, float, str]:
    """Read file and return its metadata including checksum and size."""
    size = os.path.getsize(src)
    mtime = os.path.getmtime(src)
    file_hash = hash_file(src, hash_algo=hash_algo)
    return (file_hash, size, mtime, src)


def match_extension(extensions: Optional[List[str]], fn: str) -> bool:
    """Returns true if extensions is empty"""
    if not extensions:
        return True
    for included_pattern in extensions:
        # first look for an exact match
        if fn.lower().endswith(included_pattern):
            return True
        # now try a pattern match
        if fnmatch.fnmatch(fn.lower(), included_pattern):
            return True
    return False


def clean_extensions(extensions: Optional[List[str]]) -> List[str]:
    """Cleans and normalizes a list of file extensions."""
    clean: List[str] = []
    if extensions is not None:
        for ext in extensions:
            ext = ext.strip().lower()
            if ext == ".":
                clean.append("*.")
            elif ext.startswith("*"):
                clean.append(ext)
            elif ext.startswith("."):
                clean.append(f"*{ext}")
            else:
                clean.append(f"*.{ext}")
    return clean
