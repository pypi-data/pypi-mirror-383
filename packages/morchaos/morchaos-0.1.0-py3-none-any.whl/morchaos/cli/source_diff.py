"""CLI for source code duplicate detection with whitespace normalization."""

import sys
from pathlib import Path

try:
    import click
except ImportError as e:
    raise ImportError("Required package not installed. Run: pip install click") from e

from ..logger import init_logging, logger
from ..core.source import find_source_duplicates
from ..core.file_utils import safe_path


@click.command()
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Directory to scan for source code duplicates",
)
@click.option(
    "--extensions",
    "-e",
    multiple=True,
    default=[".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go", ".rs", ".sql"],
    help="Source file extensions to include",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(directory: Path, extensions: tuple[str, ...], verbose: bool) -> None:
    """Find duplicate source code files using normalized comparison."""

    # Initialize logging
    init_logging(level=20 if verbose else 30)  # DEBUG if verbose, else WARNING

    try:
        # Validate inputs
        root_path = safe_path(directory)

        # Find source duplicates
        logger.info(f"Scanning for source code duplicates in: {root_path}")
        logger.info(f"Including extensions: {', '.join(extensions)}")

        duplicate_groups = find_source_duplicates(root_path, extensions)

        if not duplicate_groups:
            click.echo("No duplicate source files found.")
            return

        # Count total duplicates
        total_files = sum(len(paths) for paths in duplicate_groups.values())
        total_groups = len(duplicate_groups)

        click.echo(
            f"Found {total_files} duplicate source files in {total_groups} groups:"
        )

        # Display results
        for i, (file_hash, file_paths) in enumerate(duplicate_groups.items(), 1):
            click.echo(f"\nGroup {i} (normalized hash: {file_hash[:12]}...):")
            for path in file_paths:
                try:
                    # Get file size and line count for additional info
                    size_kb = path.stat().st_size / 1024
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        line_count = sum(1 for _ in f)
                    click.echo(f"  {path} ({size_kb:.1f} KB, {line_count} lines)")
                except (OSError, UnicodeDecodeError):
                    click.echo(f"  {path}")

        # Summary
        click.echo(f"\nSummary:")
        click.echo(f"  Total groups: {total_groups}")
        click.echo(f"  Total duplicate files: {total_files}")
        click.echo(f"  Extensions scanned: {', '.join(extensions)}")

        # Potential savings calculation
        total_size = 0
        duplicate_size = 0

        for file_paths in duplicate_groups.values():
            for i, path in enumerate(file_paths):
                try:
                    size = path.stat().st_size
                    total_size += size
                    if i > 0:  # Count duplicates (keep first file)
                        duplicate_size += size
                except OSError:
                    continue

        if duplicate_size > 0:
            click.echo(
                f"  Potential space savings: {duplicate_size / (1024*1024):.2f} MB"
            )

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
