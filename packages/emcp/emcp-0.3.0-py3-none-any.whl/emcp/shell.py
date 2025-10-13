import sys
import subprocess
from .utils import CommandDenied, CommandForbidden
from . import config


def shell_run(command: str, arguments: list[str]):
    if config.shell_whitelist is not None and command not in config.shell_whitelist:
        raise CommandForbidden(command=command)

    result = subprocess.run(
        [command] + arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    output = result.stdout if result.stdout.strip() else "(no output)"

    if result.returncode != 0:
        return f"Error (exit code {result.returncode}):\n{output}"

    return f"Success (exit code 0):\n{output}"
