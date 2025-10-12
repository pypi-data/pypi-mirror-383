import sys
import subprocess
from .utils import CommandDenied, CommandForbidden


def shell_run(command: str, arguments: list[str]):
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
