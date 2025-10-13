import pytest
from pathlib import Path
from emcp.fs import fs_rm
from emcp.utils import PathDoesNotExist, PathOutsideWorkDir


def test_fs_rm_file(tmp_wd):
    """fs_rm deletes a file without confirmation."""
    test_file = tmp_wd / "delete_me.txt"
    test_file.write_text("content")

    result = fs_rm(str(test_file))

    assert not test_file.exists()
    assert "Successfully deleted file" in result


def test_fs_rm_empty_directory(tmp_wd):
    """fs_rm deletes empty directory without confirmation."""
    test_dir = tmp_wd / "empty_dir"
    test_dir.mkdir()

    result = fs_rm(str(test_dir))

    assert not test_dir.exists()
    assert "Successfully deleted directory" in result


def test_fs_rm_directory_with_contents(tmp_wd):
    """fs_rm recursively deletes directory and all contents."""
    test_dir = tmp_wd / "dir_with_stuff"
    test_dir.mkdir()
    (test_dir / "file1.txt").write_text("content1")
    (test_dir / "file2.txt").write_text("content2")
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "nested.txt").write_text("nested")

    result = fs_rm(str(test_dir))

    assert not test_dir.exists()
    assert "Successfully deleted directory" in result
    assert "all its contents" in result


def test_fs_rm_nonexistent(tmp_wd):
    """fs_rm raises error for nonexistent path."""
    nonexistent = tmp_wd / "does_not_exist"

    with pytest.raises(PathDoesNotExist):
        fs_rm(str(nonexistent))


def test_fs_rm_outside_wd(tmp_path):
    """fs_rm raises error for paths outside working directory."""
    outside = tmp_path / "outside.txt"
    outside.write_text("content")

    with pytest.raises(PathOutsideWorkDir):
        fs_rm(str(outside))

    assert outside.exists()
