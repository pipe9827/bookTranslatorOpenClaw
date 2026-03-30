"""Utility functions for reading and writing files."""

from pathlib import Path


def read_file(path: str | Path) -> str:
    """Read the text content of a file.

    Args:
        path: Path to the file to read.

    Returns:
        The file content as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return Path(path).read_text(encoding="utf-8")


def write_file(path: str | Path, content: str) -> None:
    """Write text content to a file, creating parent directories as needed.

    Args:
        path: Destination file path.
        content: Text content to write.
    """
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
