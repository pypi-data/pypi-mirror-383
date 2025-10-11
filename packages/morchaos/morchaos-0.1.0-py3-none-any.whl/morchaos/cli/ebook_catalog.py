"""CLI for ebook catalogization by author."""

import sys
from pathlib import Path

try:
    import click
except ImportError as e:
    raise ImportError("Required package not installed. Run: pip install click") from e

from ..logger import init_logging, logger
from ..core.ebook import catalogize, extract_ebook_metadata
from ..core.file_utils import safe_path


@click.command()
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Directory containing ebooks to catalogize",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Show what would be done without actually moving files",
)
@click.option(
    "--preview",
    "-p",
    is_flag=True,
    help="Preview metadata extraction for files in directory",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(directory: Path, dry_run: bool, preview: bool, verbose: bool) -> None:
    """Organize ebooks into author-based directory structure."""

    # Initialize logging
    init_logging(level=20 if verbose else 30)  # DEBUG if verbose, else WARNING

    try:
        # Validate inputs
        root_path = safe_path(directory)

        if preview:
            # Preview mode: show metadata for all ebooks
            supported_extensions = {".pdf", ".epub", ".mobi", ".docx"}

            click.echo(f"Previewing ebook metadata in: {root_path}\n")

            found_files = 0
            for file_path in root_path.rglob("*"):
                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() not in supported_extensions:
                    continue

                found_files += 1
                try:
                    metadata = extract_ebook_metadata(file_path)
                    click.echo(f"File: {file_path.name}")
                    click.echo(f"  Author: {metadata['author'] or 'Unknown'}")
                    click.echo(f"  Title: {metadata['title'] or 'Unknown'}")
                    click.echo(f"  Format: {metadata['format']}")
                    click.echo()
                except Exception as e:
                    click.echo(f"File: {file_path.name}")
                    click.echo(f"  Error: {e}")
                    click.echo()

            if found_files == 0:
                click.echo("No supported ebook files found.")
            else:
                click.echo(f"Found {found_files} ebook files.")

            return

        # Catalogize mode
        action_text = "Would organize" if dry_run else "Organizing"
        click.echo(f"{action_text} ebooks in: {root_path}")

        if dry_run:
            click.echo("(Dry run mode - no files will be moved)")

        processed_count = catalogize(root_path, dry_run=dry_run)

        if processed_count == 0:
            click.echo("No ebooks found to catalogize.")
        else:
            action_text = "Would process" if dry_run else "Processed"
            click.echo(f"\n{action_text} {processed_count} ebook files.")

            if not dry_run:
                click.echo("\nCatalogization complete!")
                click.echo("Ebooks have been organized into author directories.")

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
