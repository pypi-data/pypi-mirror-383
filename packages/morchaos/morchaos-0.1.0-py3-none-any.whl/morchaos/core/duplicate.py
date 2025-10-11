"""SHA‑256 duplicate file detection and management."""
# --------------------------------------------------------------------------------
# Design concept
# --------------------------------------------------------------------------------
# 1. *Pure functions with side‑effects only in act_on_duplicates* –
#    The module separates the detection (`find_duplicates`) from the
#    destructive operations (`act_on_duplicates`).  This keeps the
#    algorithm testable and prevents accidental file changes.
#
# 2. *Chunked hashing* –  The helper `_calculate_file_hash` reads
#    files in 64 KB chunks so that even very large files do not
#    exhaust memory.  The SHA‑256 algorithm is collision‑safe for
#    file‑deduplication purposes.
#
# 3. *Flexible filtering* –  Users can supply a list of extensions
#    or `*` for “everything”, and a list of directory names to
#    ignore.  These are processed into sets for O(1) look‑ups.
#
# 4. *Graceful error handling* –  File‑access errors are logged
#    and simply skip the offending file; the overall scan continues.
#
# 5. *Safe duplicate action* –  When moving, the code resolves
#    name conflicts by appending an incrementing suffix.  The
#    caller must supply a target directory; otherwise a ValueError
#    is raised.
# --------------------------------------------------------------------------------

import hashlib
import logging
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional

logger = logging.getLogger(__name__)


def _calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA‑256 hash of a file.

    The function opens the file in binary mode and updates the
    hash object with 64 KB chunks until the EOF.  A hex digest
    is returned, or an empty string if the file could not be read.
    """
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read in 64KB chunks to manage memory usage
            for chunk in iter(lambda: f.read(65536), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except (OSError, IOError) as e:
        logger.error(f"Failed to hash file {file_path}: {e}")
        return ""


def find_duplicates(
    root: Path,
    extensions: Iterable[str] = ("*",),
    ignore_dirs: Iterable[str] = (),
) -> Dict[str, List[Path]]:
    """Find duplicate files by SHA‑256 hash.

    The routine walks ``root`` recursively, skips any files in the
    directories listed in ``ignore_dirs``, and collects files whose
    extensions match the supplied ``extensions`` set.  For each
    eligible file, the SHA‑256 hash is calculated.  The return
    value is a mapping from hash to a list of all file paths that
    share that hash; only groups with two or more entries are kept
    (i.e., true duplicates).
    """
    if not root.exists():
        raise FileNotFoundError(f"Root directory not found: {root}")
    file_hashes: Dict[str, List[Path]] = {}
    ignore_set = set(ignore_dirs)
    # Convert extensions to set for faster lookup
    ext_set = set(extensions)
    include_all = "*" in ext_set
    for file_path in root.rglob("*"):
        # Skip directories and files in ignored directories
        if file_path.is_dir():
            continue
        if any(part in ignore_set for part in file_path.parts):
            continue
        # Check file extension
        if not include_all and file_path.suffix.lower() not in ext_set:
            continue
        file_hash = _calculate_file_hash(file_path)
        if file_hash:  # Only add if hash was calculated successfully
            if file_hash not in file_hashes:
                file_hashes[file_hash] = []
            file_hashes[file_hash].append(file_path)
    # Return only groups with duplicates (2+ files)
    return {
        hash_val: paths for hash_val, paths in file_hashes.items() if len(paths) >= 2
    }


def act_on_duplicates(
    groups: Dict[str, List[Path]],
    action: Literal["delete", "move"],
    target_dir: Optional[Path] = None,
) -> int:
    """Delete or move duplicate files.

    The function iterates over each duplicate group produced by
    ``find_duplicates``.  Within each group the *first* file is
    preserved as the canonical copy; every subsequent file is
    either deleted or moved to ``target_dir`` depending on the
    ``action`` argument.  Move operations create the target
    directory if necessary and resolve filename clashes by
    appending an underscore‑separated counter.  The return value
    is the total number of files that were processed (deleted or
    moved).  A ValueError is raised if the caller requests a move
    action but does not provide a destination directory.
    """
    if action == "move" and target_dir is None:
        raise ValueError("target_dir is required when action is 'move'")
    if action == "move" and target_dir:
        target_dir.mkdir(parents=True, exist_ok=True)
    processed_count = 0
    for file_hash, file_paths in groups.items():
        # Keep the first file, process the rest
        for duplicate_path in file_paths[1:]:
            try:
                if action == "delete":
                    duplicate_path.unlink()
                    logger.info(f"Deleted duplicate: {duplicate_path}")
                elif action == "move" and target_dir:
                    dest_path = target_dir / duplicate_path.name
                    # Handle name conflicts
                    counter = 1
                    while dest_path.exists():
                        stem = duplicate_path.stem
                        suffix = duplicate_path.suffix
                        dest_path = target_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    shutil.move(str(duplicate_path), str(dest_path))
                    logger.info(f"Moved duplicate: {duplicate_path} -> {dest_path}")
                processed_count += 1
            except (OSError, IOError) as e:
                logger.error(f"Failed to {action} file {duplicate_path}: {e}")
    return processed_count
