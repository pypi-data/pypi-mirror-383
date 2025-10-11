"""CLI for duplicate file detection and management."""

import sys
from pathlib import Path
from typing import Optional

try:
    import click
except ImportError as e:
    raise ImportError("Required package not installed. Run: pip install click") from e

from ..logger import init_logging, logger
from ..core.duplicate import find_duplicates, act_on_duplicates
from ..core.file_utils import safe_path


@click.command()
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Directory to scan for duplicates",
)
@click.option(
    "--extensions",
    "-e",
    multiple=True,
    default=["*"],
    help="File extensions to include (default: all files)",
)
@click.option(
    "--ignore-dirs", "-i", multiple=True, default=[], help="Directory names to ignore"
)
@click.option(
    "--action",
    "-a",
    type=click.Choice(["list", "delete", "move"]),
    default="list",
    help="Action to perform on duplicates",
)
@click.option(
    "--target-dir",
    "-t",
    type=click.Path(path_type=Path),
    help="Target directory for move action",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(
    directory: Path,
    extensions: tuple[str, ...],
    ignore_dirs: tuple[str, ...],
    action: str,
    target_dir: Optional[Path],
    verbose: bool,
) -> None:
    """Find and manage duplicate files based on SHA-256 hash."""

    # Initialize logging
    init_logging(level=20 if verbose else 30)  # DEBUG if verbose, else WARNING

    try:
        # Validate inputs
        root_path = safe_path(directory)

        if action == "move" and not target_dir:
            click.echo(
                "Error: --target-dir is required when action is 'move'", err=True
            )
            sys.exit(2)

        if target_dir:
            target_path = safe_path(target_dir)
        else:
            target_path = None

        # Find duplicates
        logger.info(f"Scanning for duplicates in: {root_path}")
        duplicate_groups = find_duplicates(root_path, extensions, ignore_dirs)

        if not duplicate_groups:
            click.echo("No duplicates found.")
            return

        # Count total duplicates
        total_files = sum(len(paths) for paths in duplicate_groups.values())
        total_groups = len(duplicate_groups)

        click.echo(f"Found {total_files} duplicate files in {total_groups} groups:")

        # Display results
        for i, (file_hash, file_paths) in enumerate(duplicate_groups.items(), 1):
            click.echo(f"\nGroup {i} (hash: {file_hash[:12]}...):")
            for path in file_paths:
                click.echo(f"  {path}")

        # Perform action
        if action == "list":
            return
        elif action in ["delete", "move"]:
            if not click.confirm(f"\nProceed to {action} duplicate files?"):
                click.echo("Operation cancelled.")
                return

            processed = act_on_duplicates(duplicate_groups, action, target_path)  # type: ignore[arg-type]
            click.echo(f"\n{action.capitalize()}d {processed} duplicate files.")

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
