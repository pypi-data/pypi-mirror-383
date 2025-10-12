import sys
import subprocess
from .utils import CommandDenied, CommandForbidden


shell_allowed = []
shell_forbidden = []


def shell_run(command: str, arguments: list[str]):
    if command not in shell_allowed:
        if command in shell_forbidden:
            raise CommandForbidden(command=command)

        # Ask for permission
        print(f"\nAllow command '{command}'?", file=sys.stderr)
        print("  [Y] Yes | [N] No | [A] Always | [X]Never", file=sys.stderr)

        response = input("> ").strip().upper()

        if response == 'A': # always
            shell_allowed.append(command)

        elif response == 'Y': # yes, this time
            pass

        elif response == 'N': # not, not this time
            raise CommandDenied(command=command)

        elif response == 'X': # never
            shell_forbidden.append(command)
            raise CommandDenied(command=command)

        else: # no by default
            raise CommandDenied(command=command)

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
