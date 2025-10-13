import pytest
from pathlib import Path
from emcp.fs import fs_replace
from emcp.utils import FailedReplace


def test_fs_replace_single_occurrence(tmp_wd):
    """fs_replace replaces first occurrence by default."""
    test_file = tmp_wd / "test.txt"
    test_file.write_text("hello world\nhello again\n")

    result = fs_replace(str(test_file), "hello", "goodbye")

    content = test_file.read_text()
    assert content == "goodbye world\nhello again\n"
    assert result == "Made 1 replacements"


def test_fs_replace_all_occurrences(tmp_wd):
    """fs_replace replaces all occurrences when replace_all is True."""
    test_file = tmp_wd / "test.txt"
    test_file.write_text("hello world\nhello again\nhello there\n")

    result = fs_replace(str(test_file), "hello", "goodbye", replace_all=True)

    content = test_file.read_text()
    assert content == "goodbye world\ngoodbye again\ngoodbye there\n"
    assert result == "Made 3 replacements"


def test_fs_replace_multiline_string(tmp_wd):
    """fs_replace can replace multiline strings."""
    test_file = tmp_wd / "test.txt"
    test_file.write_text("line 1\nline 2\nline 3\n")

    result = fs_replace(str(test_file), "line 1\nline 2", "replaced")

    content = test_file.read_text()
    assert content == "replaced\nline 3\n"


def test_fs_replace_preserves_rest_of_file(tmp_wd):
    """fs_replace only changes the matched string."""
    test_file = tmp_wd / "test.txt"
    original = "prefix foo suffix\nother line\n"
    test_file.write_text(original)

    fs_replace(str(test_file), "foo", "bar")

    content = test_file.read_text()
    assert content == "prefix bar suffix\nother line\n"


def test_fs_replace_empty_old_string(tmp_wd):
    """fs_replace raises error for empty old_string."""
    test_file = tmp_wd / "test.txt"
    test_file.write_text("content")

    with pytest.raises(FailedReplace, match="non-empty string"):
        fs_replace(str(test_file), "", "new")


def test_fs_replace_same_strings(tmp_wd):
    """fs_replace raises error when old and new are identical."""
    test_file = tmp_wd / "test.txt"
    test_file.write_text("content")

    with pytest.raises(FailedReplace, match="must be different"):
        fs_replace(str(test_file), "same", "same")


def test_fs_replace_string_not_found(tmp_wd):
    """fs_replace raises error when old_string not found."""
    test_file = tmp_wd / "test.txt"
    original = "hello world"
    test_file.write_text(original)

    with pytest.raises(FailedReplace, match="not found"):
        fs_replace(str(test_file), "nonexistent", "replacement")

    assert test_file.read_text() == original


def test_fs_replace_nonexistent_file(tmp_wd):
    """fs_replace raises error for nonexistent file."""
    nonexistent = tmp_wd / "does_not_exist.txt"

    with pytest.raises(FailedReplace, match="Error reading file"):
        fs_replace(str(nonexistent), "old", "new")
