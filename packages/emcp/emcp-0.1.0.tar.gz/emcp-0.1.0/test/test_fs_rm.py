import pytest
from pathlib import Path
from emcp.fs import fs_rm
from emcp.utils import CommandDenied, PathDoesNotExist, PathOutsideWorkDir


def test_fs_rm_file(tmp_wd):
    """fs_rm deletes a file without confirmation."""
    test_file = tmp_wd / "delete_me.txt"
    test_file.write_text("content")

    result = fs_rm(str(test_file))

    assert not test_file.exists()
    assert "Successfully deleted file" in result


def test_fs_rm_empty_directory_with_confirmation(tmp_wd, monkeypatch):
    """fs_rm deletes empty directory with user confirmation."""
    test_dir = tmp_wd / "empty_dir"
    test_dir.mkdir()

    monkeypatch.setattr('builtins.input', lambda prompt: 'Y')

    result = fs_rm(str(test_dir))

    assert not test_dir.exists()
    assert "Successfully deleted directory" in result


def test_fs_rm_directory_with_contents(tmp_wd, monkeypatch):
    """fs_rm recursively deletes directory and all contents with confirmation."""
    test_dir = tmp_wd / "dir_with_stuff"
    test_dir.mkdir()
    (test_dir / "file1.txt").write_text("content1")
    (test_dir / "file2.txt").write_text("content2")
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "nested.txt").write_text("nested")

    monkeypatch.setattr('builtins.input', lambda prompt: 'Y')

    result = fs_rm(str(test_dir))

    assert not test_dir.exists()
    assert "Successfully deleted directory" in result
    assert "all its contents" in result


def test_fs_rm_directory_denied(tmp_wd, monkeypatch):
    """fs_rm does not delete directory when user denies."""
    test_dir = tmp_wd / "keep_me"
    test_dir.mkdir()
    (test_dir / "important.txt").write_text("important data")

    monkeypatch.setattr('builtins.input', lambda prompt: 'N')

    with pytest.raises(CommandDenied):
        fs_rm(str(test_dir))

    assert test_dir.exists()
    assert (test_dir / "important.txt").exists()


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
