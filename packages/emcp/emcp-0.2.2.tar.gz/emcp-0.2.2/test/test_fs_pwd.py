import pytest
from emcp.fs import fs_pwd


def test_fs_pwd(tmp_wd):
    """fs_pwd returns the current working directory."""
    result = fs_pwd()

    assert result == str(tmp_wd)
