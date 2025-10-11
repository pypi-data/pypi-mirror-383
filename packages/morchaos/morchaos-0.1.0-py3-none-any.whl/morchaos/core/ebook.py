"""Ebook metadata extraction and catalogization."""
import logging
import re
import shutil
from pathlib import Path
from typing import Dict, Optional

# Import third‑party libraries used for the various ebook formats.
# A clear error message is raised if any are missing.
try:
    import pdfplumber  # PDF extraction
    from docx import Document  # DOCX extraction
    import ebooklib
    from ebooklib import epub  # EPUB extraction
except ImportError as e:
    raise ImportError(
        "Required packages not installed. Run: pip install pdfplumber python-docx ebooklib"
    ) from e

# Utility to sanitise directory names (imported from local module)
from .file_utils import sanitize_filename

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Individual format‑specific metadata extractors
# ----------------------------------------------------------------------
def _extract_pdf_metadata(path: Path) -> Dict[str, str]:
    """Extract metadata from PDF file."""
    try:
        with pdfplumber.open(path) as pdf:
            metadata = pdf.metadata or {}
            return {
                "author": metadata.get("Author", "").strip(),
                "title": metadata.get("Title", "").strip(),
                "format": "pdf",
            }
    except Exception as e:
        logger.warning(f"Failed to extract PDF metadata from {path}: {e}")
        return {"author": "", "title": "", "format": "pdf"}


def _extract_epub_metadata(path: Path) -> Dict[str, str]:
    """Extract metadata from EPUB file."""
    try:
        book = epub.read_epub(str(path))
        author = ""
        title = ""
        # Try to get author and title from metadata
        for item in book.get_metadata("DC", "creator"):
            if item[0]:
                author = item[0].strip()
                break
        for item in book.get_metadata("DC", "title"):
            if item[0]:
                title = item[0].strip()
                break
        return {"author": author, "title": title, "format": "epub"}
    except Exception as e:
        logger.warning(f"Failed to extract EPUB metadata from {path}: {e}")
        return {"author": "", "title": "", "format": "epub"}


def _extract_docx_metadata(path: Path) -> Dict[str, str]:
    """Extract metadata from DOCX file."""
    try:
        doc = Document(path)
        core_props = doc.core_properties
        return {
            "author": (core_props.author or "").strip(),
            "title": (core_props.title or "").strip(),
            "format": "docx",
        }
    except Exception as e:
        logger.warning(f"Failed to extract DOCX metadata from {path}: {e}")
        return {"author": "", "title": "", "format": "docx"}


# ----------------------------------------------------------------------
# Fallback helpers
# ----------------------------------------------------------------------
def _extract_from_filename(path: Path) -> str:
    """Extract author from filename using common patterns."""
    filename = path.stem
    # Common patterns: "Author - Title", "Author_Title", "Title by Author"
    patterns = [
        r"^([^-_]+)\s*[-_]\s*(.+)$",  # Author - Title or Author_Title
        r"^(.+)\s+by\s+([^-_]+)$",  # Title by Author
        r"^([^(]+)\s*\([^)]*\).*$",  # Author (anything)
    ]
    for pattern in patterns:
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            # Return the first captured group as a potential author
            return match.group(1).strip()
    # If no pattern matches, return empty string
    return ""


# ----------------------------------------------------------------------
# Unified entry point for metadata extraction
# ----------------------------------------------------------------------
def extract_ebook_metadata(path: Path) -> Dict[str, str]:
    """Extract metadata from ebook file.

    Args:
        path: Path to ebook file

    Returns:
        Dictionary with 'author', 'title', and 'format' keys
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        metadata = _extract_pdf_metadata(path)
    elif suffix == ".epub":
        metadata = _extract_epub_metadata(path)
    elif suffix == ".docx":
        metadata = _extract_docx_metadata(path)
    elif suffix == ".mobi":
        # MOBI support would require an additional library (e.g., 'mobi')
        metadata = {"author": "", "title": "", "format": "mobi"}
    else:
        metadata = {
            "author": "",
            "title": "",
            "format": suffix[1:] if suffix else "unknown",
        }
    # Fallback to filename parsing if no author found
    if not metadata["author"]:
        metadata["author"] = _extract_from_filename(path)
    # Use filename as title if no title found
    if not metadata["title"]:
        metadata["title"] = path.stem
    return metadata


# ----------------------------------------------------------------------
# Catalogisation logic – organise books into <root>/<author>/ structure
# ----------------------------------------------------------------------
def catalogize(root: Path, dry_run: bool = False) -> int:
    """Organize ebooks into author‑based directory structure.

    Moves each ebook into <root>/<author>/ preserving original filename.
    Assumes files that are already in a sub‑folder have been catalogised.

    Args:
        root: Root directory containing ebooks
        dry_run: If True, only log actions without moving files

    Returns:
        Number of files processed

    Raises:
        FileNotFoundError: If root directory doesn't exist
    """
    if not root.exists():
        raise FileNotFoundError(f"Root directory not found: {root}")

    supported_extensions = {".pdf", ".epub", ".mobi", ".docx"}
    processed_count = 0

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in supported_extensions:
            continue
        # Skip files already in subdirectories (assume already catalogized)
        if file_path.parent != root:
            continue
        try:
            metadata = extract_ebook_metadata(file_path)
            author = metadata["author"]
            # Normalise author values that are empty / generic
            if not author or author.lower() in ["unknown", "anonymous", ""]:
                author = "Unknown_Author"
            # Sanitize author name for use as a directory
            author_dir = sanitize_filename(author)
            target_dir = root / author_dir
            if dry_run:
                logger.info(f"Would move: {file_path} -> {target_dir / file_path.name}")
            else:
                # Create author directory if missing
                target_dir.mkdir(exist_ok=True)
                target_path = target_dir / file_path.name
                # Resolve naming conflicts by appending a counter
                counter = 1
                while target_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    target_path = target_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                shutil.move(str(file_path), str(target_path))
                logger.info(f"Moved: {file_path} -> {target_path}")
            processed_count += 1
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
    return processed_count
