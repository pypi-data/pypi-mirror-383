"""CLI for image duplicate detection using perceptual hashing."""

import sys
from pathlib import Path

try:
    import click
except ImportError as e:
    raise ImportError("Required package not installed. Run: pip install click") from e

from ..logger import init_logging, logger
from ..core.image import find_image_duplicates
from ..core.file_utils import safe_path


@click.command()
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Directory to scan for image duplicates",
)
@click.option(
    "--extensions",
    "-e",
    multiple=True,
    default=[".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"],
    help="Image file extensions to include",
)
@click.option(
    "--threshold",
    "-t",
    type=int,
    default=5,
    help="Similarity threshold (0-64, lower = more strict)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(
    directory: Path, extensions: tuple[str, ...], threshold: int, verbose: bool
) -> None:
    """Find duplicate images using perceptual hashing."""

    # Initialize logging
    init_logging(level=20 if verbose else 30)  # DEBUG if verbose, else WARNING

    try:
        # Validate inputs
        root_path = safe_path(directory)

        if not 0 <= threshold <= 64:
            click.echo("Error: threshold must be between 0 and 64", err=True)
            sys.exit(2)

        # Find image duplicates
        logger.info(f"Scanning for image duplicates in: {root_path}")
        logger.info(f"Using similarity threshold: {threshold}")

        duplicate_groups = find_image_duplicates(root_path, extensions, threshold)

        if not duplicate_groups:
            click.echo("No duplicate images found.")
            return

        # Count total duplicates
        total_files = sum(len(paths) for paths in duplicate_groups.values())
        total_groups = len(duplicate_groups)

        click.echo(f"Found {total_files} similar images in {total_groups} groups:")

        # Display results
        for i, (phash, file_paths) in enumerate(duplicate_groups.items(), 1):
            click.echo(f"\nGroup {i} (phash: {phash}):")
            for path in file_paths:
                try:
                    # Get file size for additional info
                    size_mb = path.stat().st_size / (1024 * 1024)
                    click.echo(f"  {path} ({size_mb:.2f} MB)")
                except OSError:
                    click.echo(f"  {path}")

        # Summary
        click.echo(f"\nSummary:")
        click.echo(f"  Total groups: {total_groups}")
        click.echo(f"  Total similar images: {total_files}")
        click.echo(f"  Similarity threshold: {threshold}")

    except (ValueError, FileNotFoundError) as e:
        logger.error(str(e))
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
