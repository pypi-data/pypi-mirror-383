import pytest
from unittest.mock import Mock
from emcp.shell import shell_run
from emcp.utils import CommandForbidden


def test_shell_command_default_restrictions(mock_subprocess):
    """shell executes command when no restrictions are enabled."""
    result = shell_run('ls', ['-la'])

    assert result == "Success (exit code 0):\nmock output"
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args[0][0]
    assert call_args == ['ls', '-la']


def test_shell_command_with_restrictions_allowed(mock_subprocess, monkeypatch):
    """shell executes command when restrictions enabled and command is allowed."""
    monkeypatch.setattr('emcp.config.shell_whitelist', {'git', 'ls'})

    result = shell_run('git', ['status'])

    assert result == "Success (exit code 0):\nmock output"
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args[0][0]
    assert call_args == ['git', 'status']


def test_shell_command_with_restrictions_forbidden(mock_subprocess, monkeypatch):
    """shell raises CommandForbidden when restrictions enabled and command not allowed."""
    monkeypatch.setattr('emcp.config.shell_whitelist', {'git', 'ls'})

    with pytest.raises(CommandForbidden):
        shell_run('rm', ['-rf'])

    mock_subprocess.assert_not_called()


def test_shell_command_restrictions_disabled(mock_subprocess, monkeypatch):
    """shell executes any command when restrictions are disabled."""
    monkeypatch.setattr('emcp.config.shell_whitelist', None)

    result = shell_run('any_command', ['args'])

    assert result == "Success (exit code 0):\nmock output"
    mock_subprocess.assert_called_once()


def test_shell_nonzero_exit_code(mock_subprocess):
    """shell returns error message for non-zero exit codes."""
    mock_subprocess.return_value = Mock(
        returncode=1,
        stdout="error output",
        stderr=""
    )

    result = shell_run('failing', ['command'])

    assert result.startswith("Error (exit code 1):")
    assert "error output" in result


def test_shell_empty_output(mock_subprocess):
    """shell handles empty stdout."""
    mock_subprocess.return_value = Mock(
        returncode=0,
        stdout="",
        stderr=""
    )

    result = shell_run('silent', ['command'])

    assert result == "Success (exit code 0):\n(no output)"


def test_shell_arguments_passed_correctly(mock_subprocess):
    """shell passes arguments to subprocess correctly."""
    shell_run('cmd', ['arg1', 'arg2', 'arg3'])

    call_args = mock_subprocess.call_args[0][0]
    assert call_args == ['cmd', 'arg1', 'arg2', 'arg3']
