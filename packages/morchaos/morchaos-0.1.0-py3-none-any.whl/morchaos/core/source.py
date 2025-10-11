"""Whitespace‑insensitive source code duplicate detection."""
# ------------------------------------------------------------------
# Design Concept
# ----------------
# 1. The goal is to detect source‑code files that are *functionally*
#    identical even if they differ in whitespace, comments, or minor
#    formatting.  To achieve this, each file is **normalized**:
#    * comments are stripped (style depends on the file type)
#    * all whitespace runs are collapsed into a single space
#    * leading/trailing whitespace is removed
#    * unnecessary spaces around punctuation are removed
# 2. The normalized text is hashed with MD5 – a deterministic,
#    inexpensive fingerprint that can be compared quickly.
# 3. Files are scanned recursively under a root directory, and
#    groups of files sharing the same hash are reported as duplicates.
# 4. Error handling is intentionally tolerant: unreadable files
#    are logged and skipped; missing directories raise an exception.
#
# Complexity
# -----------
# - Let N be the number of files under *root*, and L the average file
#   size.  Normalization and hashing run in O(L) per file.
# - The algorithm is essentially linear in total input size
#   (O(∑L)).  Hash‑map lookups keep duplicate grouping at O(1)
#   amortised per file.
# ------------------------------------------------------------------

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, List

logger = logging.getLogger(__name__)


def normalize_hash(path: Path) -> str:
    """Calculate normalized hash for a source‑code file.

    The function opens the file, normalises its contents
    (removing comments/whitespace) via ``_normalize_source_content``,
    then hashes the result with MD5.

    Args:
        path: Path to source‑code file.

    Returns:
        MD5 hex digest of the normalized content.

    Raises:
        ValueError: If the file cannot be read or processed.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError) as e:
        logger.error(f"Failed to read file {path}: {e}")
        raise ValueError(f"Cannot read source file: {path}") from e

    # Normalize the content: strip comments, collapse whitespace, etc.
    normalized = _normalize_source_content(content, path.suffix)

    # Calculate MD5 hash of the normalised string
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def _normalize_source_content(content: str, file_extension: str) -> str:
    """Normalize source‑code content for comparison.

    This helper removes comments based on the file extension and
    collapses/normalises whitespace to a canonical form.
    The goal is to ensure that two semantically identical files
    produce the same hash even if they differ in formatting.

    Args:
        content: Raw source‑code text.
        file_extension: Extension used to infer comment syntax.

    Returns:
        A single string that represents the *semantic* content
        of the source file.
    """
    # Remove comments based on file type
    if file_extension in [".py", ".sh", ".bash"]:
        # Python / shell style comments start with '#'
        content = re.sub(r"#.*$", "", content, flags=re.MULTILINE)
    elif file_extension in [".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go", ".rs"]:
        # C‑style comments: single line '//' and multi‑line '/* */'
        content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)  # single line
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)  # multi line
    elif file_extension in [".html", ".xml"]:
        # HTML / XML comments: <!-- comment -->
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    elif file_extension in [".sql"]:
        # SQL comments: '--' or '/* */'
        content = re.sub(r"--.*$", "", content, flags=re.MULTILINE)
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

    # Replace any run of whitespace (spaces, tabs, newlines) with a single space
    content = re.sub(r"\s+", " ", content)
    # Strip leading/trailing whitespace
    content = content.strip()

    # Remove extraneous spaces around parentheses, commas, and quotes
    content = re.sub(r"\s*\(\s*", "(", content)
    content = re.sub(r"\s*\)\s*", ")", content)
    content = re.sub(r"\s*,\s*", ",", content)

    return content


def find_source_duplicates(
    root: Path,
    extensions: Iterable[str] = (
        ".py",
        ".js",
        ".ts",
        ".java",
        ".c",
        ".cpp",
        ".cs",
        ".go",
        ".rs",
        ".sql",
    ),
) -> Dict[str, List[Path]]:
    """Find duplicate source‑code files using normalized hashing.

    The routine walks the *root* directory recursively,
    hashes each eligible file with ``normalize_hash``, and
    groups paths by their hash value.  Only groups containing
    at least two files are returned.

    Args:
        root: Root directory to search.
        extensions: File extensions to include; case‑insensitive.

    Returns:
        A mapping from MD5 hash to a list of Paths that share that
        hash (i.e., are considered duplicates).

    Raises:
        FileNotFoundError: If the *root* directory does not exist.
    """
    if not root.exists():
        raise FileNotFoundError(f"Root directory not found: {root}")

    # Mapping: hash → list of Paths that produce that hash
    source_hashes: Dict[str, List[Path]] = {}
    # Normalise extension lookup to lower‑case
    ext_set = {ext.lower() for ext in extensions}

    # ------------------------------------------------------------------
    # Walk all files under *root* recursively
    # ------------------------------------------------------------------
    for file_path in root.rglob("*"):
        # Skip directories and non‑matching extensions
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in ext_set:
            continue

        # Compute hash; skip unreadable files gracefully
        try:
            file_hash = normalize_hash(file_path)
            if file_hash not in source_hashes:
                source_hashes[file_hash] = []
            source_hashes[file_hash].append(file_path)
        except ValueError:
            # Log the issue and continue with next file
            logger.warning(f"Skipping unreadable file: {file_path}")
            continue

    # ------------------------------------------------------------------
    # Filter out hash groups that contain only a single file
    # ------------------------------------------------------------------
    return {
        hash_val: paths for hash_val, paths in source_hashes.items() if len(paths) >= 2
    }
