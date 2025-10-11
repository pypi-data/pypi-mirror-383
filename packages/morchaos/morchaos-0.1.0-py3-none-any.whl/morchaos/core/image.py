"""Perceptual hash‑based image duplicate detection."""
# --------------------------------------------------------------------------
# Design concept
# --------------------------------------------------------------------------
# 1. *Pure functional interface* –  All public functions (`phash_for_file`,
#    `find_image_duplicates`) return data structures and raise well‑defined
#    exceptions.  They do not perform any I/O other than reading images, so
#    callers can easily unit‑test the logic.
#
# 2. *Lazy imports* –  The heavy dependencies (`imagehash`, `Pillow`) are
#    imported inside a try/except block.  This allows the module to be
#    imported even when the optional dependencies are missing; the user
#    receives an explicit error message at import time.
#
# 3. *Robust error handling* –  Any problem opening or hashing an image
#    results in a logged error and a `ValueError`.  This keeps the
#    scanning loop robust: a single corrupted file does not abort the
#    entire duplicate search.
#
# 4. *Two‑pass strategy* –  First we build a dictionary of exact perceptual
#    hashes.  In the second pass we optionally merge hashes that are
#    within a given Hamming‑distance threshold.  This keeps the logic
#    simple and allows callers to choose strict (exact match) or relaxed
#    (similar match) duplicate detection.
#
# 5. *Efficiency considerations* –  We store paths in lists keyed by hash
#    so that grouping is O(n²) only in the second pass when `threshold`
#    > 0.  For typical workloads (hundreds of images) this is fine; for
#    very large sets a more advanced clustering algorithm could be used.
# --------------------------------------------------------------------------


import logging
from pathlib import Path
from typing import Dict, Iterable, List

# Optional third‑party imports – provide a helpful message if missing
try:
    import imagehash
    from PIL import Image
except ImportError as e:
    raise ImportError(
        "Required packages not installed. Run: pip install imagehash Pillow"
    ) from e

# Local logger – callers can configure the root logger as needed
logger = logging.getLogger(__name__)


def phash_for_file(path: Path) -> str:
    """Calculate perceptual hash for an image file.

    The function opens the image, ensures it is in RGB mode (so the hash is
    consistent across formats), and then computes a 64‑bit perceptual hash.

    Args:
        path: Path to image file

    Returns:
        64‑bit perceptual hash as hex string

    Raises:
        ValueError: If file cannot be processed as an image
    """
    try:
        # Pillow's context manager automatically closes the file descriptor
        with Image.open(path) as img:
            # Convert to RGB if necessary – some formats store pixels in
            # palette or grayscale which would give a different hash.
            if img.mode != "RGB":
                img = img.convert("RGB")
            # Calculate perceptual hash using the default phash algorithm
            phash = imagehash.phash(img)
            return str(phash)
    except Exception as e:
        # Log the failure and re‑raise as ValueError so callers can
        # distinguish image‑processing errors from other failures.
        logger.error(f"Failed to calculate phash for {path}: {e}")
        raise ValueError(f"Cannot process image file: {path}") from e


def find_image_duplicates(
    root: Path,
    extensions: Iterable[str] = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"),
    threshold: int = 5,
) -> Dict[str, List[Path]]:
    """Find duplicate images using perceptual hashing.

    The routine walks the directory tree rooted at ``root``, hashes all
    supported image files, and groups paths that either share the exact
    hash or fall within a given Hamming‑distance threshold.

    Args:
        root: Root directory to search
        extensions: Image file extensions to include (case‑insensitive)
        threshold: Hamming distance threshold for similarity (lower = more strict)

    Returns:
        Mapping of representative hash to list of similar images

    Raises:
        FileNotFoundError: If root directory doesn't exist
    """
    # Defensive check – avoid walking a non‑existent directory
    if not root.exists():
        raise FileNotFoundError(f"Root directory not found: {root}")

    # First pass: compute exact hashes for all image files
    image_hashes: Dict[str, List[Path]] = {}
    ext_set = {ext.lower() for ext in extensions}

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in ext_set:
            continue
        try:
            phash = phash_for_file(file_path)
            image_hashes.setdefault(phash, []).append(file_path)
        except ValueError:
            # Skip files that cannot be processed as images
            continue

    # Second pass: merge hashes that are similar if a threshold was supplied
    if threshold > 0:
        grouped_hashes: Dict[str, List[Path]] = {}
        processed_hashes = set()

        for hash1, paths1 in image_hashes.items():
            if hash1 in processed_hashes:
                continue
            similar_group = paths1.copy()
            processed_hashes.add(hash1)

            for hash2, paths2 in image_hashes.items():
                if hash2 in processed_hashes:
                    continue
                try:
                    h1 = imagehash.hex_to_hash(hash1)
                    h2 = imagehash.hex_to_hash(hash2)
                    distance = h1 - h2
                    if distance <= threshold:
                        similar_group.extend(paths2)
                        processed_hashes.add(hash2)
                except Exception as e:
                    # Any error comparing two hashes is logged but does not
                    # abort the entire grouping process.
                    logger.warning(f"Failed to compare hashes {hash1} and {hash2}: {e}")

            if len(similar_group) >= 2:
                grouped_hashes[hash1] = similar_group

        return grouped_hashes

    # If no threshold was supplied, return only exact duplicates
    return {
        hash_val: paths for hash_val, paths in image_hashes.items() if len(paths) >= 2
    }
