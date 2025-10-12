import pytest
from pathlib import Path
from emcp.fs import fs_list
from emcp.utils import PathDoesNotExist, PathIsNotDirectory, PathOutsideWorkDir


def test_fs_list_directory(sample_dir):
    """fs_list returns directory contents with correct metadata."""
    result = fs_list(str(sample_dir))

    lines = result.split('\n')
    assert len(lines) == 3

    # Verify each entry format and content
    entries = {}
    for line in lines:
        parts = line.split()
        size = int(parts[0])
        file_type = parts[1]
        name = parts[2]
        entries[name] = (size, file_type)

    # Check files exist with correct types
    assert 'file1.txt' in entries
    assert 'file2.txt' in entries
    assert 'subdir' in entries

    # Verify types
    assert entries['file1.txt'][1] == 'f'
    assert entries['file2.txt'][1] == 'f'
    assert entries['subdir'][1] == 'd'

    # Verify sizes match actual files
    file1_stat = (sample_dir / 'file1.txt').stat()
    file2_stat = (sample_dir / 'file2.txt').stat()
    subdir_stat = (sample_dir / 'subdir').stat()

    assert entries['file1.txt'][0] == file1_stat.st_size
    assert entries['file2.txt'][0] == file2_stat.st_size
    assert entries['subdir'][0] == subdir_stat.st_size


def test_fs_list_empty_directory(tmp_wd):
    """fs_list returns empty string for empty directory."""
    empty_dir = tmp_wd / "empty"
    empty_dir.mkdir()

    result = fs_list(str(empty_dir))

    assert result == ""


def test_fs_list_current_directory(tmp_wd):
    """fs_list works with default current directory parameter."""
    # Create some files in tmp_wd
    (tmp_wd / "test.txt").write_text("content")

    result = fs_list(str(tmp_wd))

    assert "test.txt" in result


def test_fs_list_nonexistent(tmp_wd):
    """fs_list raises error for nonexistent path."""
    nonexistent = tmp_wd / "does_not_exist"

    with pytest.raises(PathDoesNotExist):
        fs_list(str(nonexistent))


def test_fs_list_not_directory(sample_file):
    """fs_list raises error when path is not a directory."""
    with pytest.raises(PathIsNotDirectory):
        fs_list(str(sample_file))


def test_fs_list_outside_wd(tmp_path):
    """fs_list raises error for paths outside working directory."""
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    with pytest.raises(PathOutsideWorkDir):
        fs_list(str(outside_dir))
