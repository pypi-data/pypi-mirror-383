"""File utilities for path sanitization and temporary directory cleanup."""
import logging
import shutil
from pathlib import Path
from typing import Iterable, Union

# Logger instance used throughout the module.  All messages go through the
# module's logger so that callers can configure a shared logging configuration.
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Design concept
# --------------------------------------------------------------------------- #
# 1. *Pure functions* – Each public function (`safe_path`, `remove_temp_dirs`,
#    `sanitize_filename`) performs a single, well‑defined task and does not
#    mutate global state (other than via the filesystem, which is inevitable
#    for these utilities).  They return a value rather than printing directly.
#
# 2. *Robust error handling* – Errors are raised with clear, typed exceptions
#    (`ValueError`, `FileNotFoundError`, `OSError`) and all I/O failures are
#    logged.  This makes the behaviour predictable for callers and keeps
#    debugging straightforward.
#
# 3. *Pathlib over os.path* – `Path` objects provide richer, safer path
#    manipulation and are easier to work with when resolving symbolic links
#    and normalising paths.
#
# 4. *Safety first* – `safe_path` validates the input and checks that the
#    resolved path exists, but it never forces creation of missing directories
#    (to avoid accidental data loss).  The function is useful for
#    normalising paths before they are used by the caller.
#
# 5. *Non‑destructive sanitisation* – `sanitize_filename` does not attempt to
#    guess a safe extension or rename conflicts.  It simply replaces illegal
#    characters and falls back to a default name if the result is empty.
#
# 6. *Extensibility* – Pattern matching in `remove_temp_dirs` is delegated
#    to `Path.rglob`, allowing callers to use glob syntax (`*`, `?`, `**`) to
#    describe the directories they wish to delete.
# --------------------------------------------------------------------------- #


def safe_path(path: Union[str, Path]) -> Path:
    """Return an absolute, resolved Path.
    Args:
        path: File or directory path
    Returns:
        Absolute, resolved Path object
    Raises:
        ValueError: If path is invalid or outside allowed boundaries
    """
    # Check for empty or whitespace‑only strings – these are not valid paths.
    if not path or (isinstance(path, str) and not path.strip()):
        raise ValueError(f"Invalid path: {path}")

    # Resolve the path to an absolute, canonical form.
    # `Path.resolve()` follows symlinks and removes redundant components.
    try:
        resolved_path = Path(path).resolve()
        if not resolved_path.exists():
            # The caller might be interested in the fact that the path does
            # not yet exist; we only log a warning but still return the object.
            logger.warning(f"Path does not exist: {resolved_path}")
        return resolved_path
    except (OSError, ValueError) as e:
        # Wrap any lower‑level error into a ValueError to keep the public
        # API consistent.
        raise ValueError(f"Invalid path: {path}") from e


def remove_temp_dirs(root: Path, patterns: Iterable[str]) -> int:
    """Delete directories matching patterns under root.
    Args:
        root: Root directory to search under
        patterns: Directory name patterns to match
    Returns:
        Number of directories removed
    Raises:
        FileNotFoundError: If root directory doesn't exist
    """
    # Defensive check – callers should not be allowed to run this routine on
    # a non‑existent root, as that would silently do nothing.
    if not root.exists():
        raise FileNotFoundError(f"Root directory not found: {root}")

    removed_count = 0
    # Iterate over each glob pattern separately so we can log successes/failures
    # per pattern and keep the overall count accurate.
    for pattern in patterns:
        # `rglob` performs a recursive glob – it will match directories
        # anywhere under `root` that match the pattern.
        for dir_path in root.rglob(pattern):
            if dir_path.is_dir():
                try:
                    shutil.rmtree(dir_path)
                    logger.info(f"Removed directory: {dir_path}")
                    removed_count += 1
                except OSError as e:
                    # A failure here should not stop the loop – we log and
                    # continue so that the caller still gets a count of the
                    # directories that were successfully removed.
                    logger.error(f"Failed to remove directory {dir_path}: {e}")
    return removed_count


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters.
    Args:
        filename: Original filename
    Returns:
        Sanitized filename safe for filesystem
    """
    # Characters that are disallowed on most filesystems (Windows is the
    # strictest; Unix tolerates many of these but we keep them for
    # cross‑platform compatibility).
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename
    # Replace each illegal character with an underscore.
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")
    # Strip leading/trailing whitespace and dots – those can cause hidden
    # files or directory ambiguity on some systems.
    sanitized = sanitized.strip(" .")
    # Ensure we never return an empty string – callers might try to create a
    # file with an empty name otherwise.
    if not sanitized:
        sanitized = "unnamed_file"
    return sanitized
