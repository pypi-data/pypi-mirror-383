import pytest
from pathlib import Path
from emcp.fs import fs_read
from emcp.utils import PathDoesNotExist, PathIsNotFile, PathOutsideWorkDir


def test_fs_read_entire_file(sample_file):
    """fs_read returns entire file contents by default."""
    result = fs_read(str(sample_file))

    expected = sample_file.read_text()
    assert result == expected


def test_fs_read_with_start(sample_file):
    """fs_read reads from start line onwards."""
    result = fs_read(str(sample_file), start=2)

    lines = sample_file.read_text().splitlines(keepends=True)
    expected = "".join(lines[2:])
    assert result == expected


def test_fs_read_with_start_and_end(sample_file):
    """fs_read reads specified line range."""
    result = fs_read(str(sample_file), start=1, end=3)

    lines = sample_file.read_text().splitlines(keepends=True)
    expected = "".join(lines[1:4])
    assert result == expected


def test_fs_read_negative_end(sample_file):
    """fs_read handles negative end index."""
    result = fs_read(str(sample_file), start=0, end=-2)

    lines = sample_file.read_text().splitlines(keepends=True)
    expected = "".join(lines[0:len(lines) - 1])
    assert result == expected


def test_fs_read_single_line(sample_file):
    """fs_read can read a single line."""
    result = fs_read(str(sample_file), start=0, end=0)

    lines = sample_file.read_text().splitlines(keepends=True)
    expected = lines[0]
    assert result == expected


def test_fs_read_nonexistent(tmp_wd):
    """fs_read raises error for nonexistent file."""
    nonexistent = tmp_wd / "does_not_exist.txt"

    with pytest.raises(PathDoesNotExist):
        fs_read(str(nonexistent))


def test_fs_read_directory(sample_dir):
    """fs_read raises error when path is a directory."""
    with pytest.raises(PathIsNotFile):
        fs_read(str(sample_dir))


def test_fs_read_outside_wd(tmp_path):
    """fs_read raises error for paths outside working directory."""
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("content")

    with pytest.raises(PathOutsideWorkDir):
        fs_read(str(outside_file))
