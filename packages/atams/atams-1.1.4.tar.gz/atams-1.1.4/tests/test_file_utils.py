"""Test file utilities"""
from pathlib import Path
from atams.utils.file_utils import (
    ensure_dir,
    write_file,
    read_file,
    file_exists,
    dir_exists
)


def test_ensure_dir(tmp_path):
    """Test directory creation"""
    test_dir = tmp_path / "test" / "nested" / "deep"
    result = ensure_dir(test_dir)

    assert result.exists()
    assert result.is_dir()
    assert result == test_dir


def test_ensure_dir_existing(tmp_path):
    """Test ensure_dir with existing directory"""
    test_dir = tmp_path / "existing"
    test_dir.mkdir()

    result = ensure_dir(test_dir)
    assert result.exists()
    assert result == test_dir


def test_write_and_read_file(tmp_path):
    """Test file write and read"""
    test_file = tmp_path / "test.txt"
    content = "Hello ATAMS Toolkit!"

    # Write file
    result = write_file(test_file, content)
    assert result == test_file
    assert test_file.exists()

    # Read file
    read_content = read_file(test_file)
    assert read_content == content


def test_write_file_creates_parent_dirs(tmp_path):
    """Test that write_file creates parent directories"""
    test_file = tmp_path / "nested" / "dir" / "test.txt"
    content = "Test content"

    write_file(test_file, content)

    assert test_file.exists()
    assert read_file(test_file) == content


def test_file_exists(tmp_path):
    """Test file existence check"""
    test_file = tmp_path / "exists.txt"

    # File doesn't exist
    assert not file_exists(test_file)

    # Create file
    test_file.write_text("content")

    # File exists
    assert file_exists(test_file)


def test_dir_exists(tmp_path):
    """Test directory existence check"""
    test_dir = tmp_path / "test_dir"

    # Directory doesn't exist
    assert not dir_exists(test_dir)

    # Create directory
    test_dir.mkdir()

    # Directory exists
    assert dir_exists(test_dir)


def test_read_file_encoding(tmp_path):
    """Test file read with UTF-8 encoding"""
    test_file = tmp_path / "unicode.txt"
    content = "Hello 世界 🌍"

    write_file(test_file, content)
    read_content = read_file(test_file)

    assert read_content == content
