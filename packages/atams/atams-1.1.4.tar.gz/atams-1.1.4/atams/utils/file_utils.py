"""
File manipulation utilities for ATAMS CLI
"""
from pathlib import Path
from typing import Optional


def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists, create if not

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_file(path: Path, content: str) -> Path:
    """
    Write content to file

    Args:
        path: File path
        content: File content

    Returns:
        Path object
    """
    # Ensure parent directory exists
    ensure_dir(path.parent)

    # Write file
    path.write_text(content, encoding='utf-8')
    return path


def read_file(path: Path) -> Optional[str]:
    """
    Read file content

    Args:
        path: File path

    Returns:
        File content or None if file doesn't exist
    """
    if not path.exists():
        return None

    return path.read_text(encoding='utf-8')


def file_exists(path: Path) -> bool:
    """
    Check if file exists

    Args:
        path: File path

    Returns:
        True if file exists
    """
    return path.exists() and path.is_file()


def dir_exists(path: Path) -> bool:
    """
    Check if directory exists

    Args:
        path: Directory path

    Returns:
        True if directory exists
    """
    return path.exists() and path.is_dir()
