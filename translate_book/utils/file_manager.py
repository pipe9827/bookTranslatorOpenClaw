"""File management utilities for the translation pipeline."""

from pathlib import Path


def read_file(path: str | Path) -> str:
    """Read the text content of a file.

    Args:
        path: Absolute or relative path to the file.

    Returns:
        The decoded text content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If the file cannot be read.
    """
    file_path = Path(path)
    return file_path.read_text(encoding="utf-8")


def write_file(path: str | Path, content: str) -> None:
    """Write text content to a file, creating parent directories as needed.

    Args:
        path: Absolute or relative path to the destination file.
        content: Text to write.

    Raises:
        OSError: If the file cannot be written.
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
