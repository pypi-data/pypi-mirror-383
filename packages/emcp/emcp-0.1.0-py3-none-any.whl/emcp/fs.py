import os
import sys
import subprocess
from pathlib import Path

from .utils import (
    PathAlreadyExists,
    PathDoesNotExist,
    PathIsNotDirectory,
    PathIsNotFile,
    PathOutsideWorkDir,
    FailedReplace,
    CommandDenied
)
from . import config


def fs_pwd() -> str:
    return config.wd


def fs_stat(path: str) -> str:
    p = Path(path)
    if not is_inside(p, config.wd): raise PathOutsideWorkDir(path=path, wd=config.wd)
    if not p.exists(): raise PathDoesNotExist(path=path)

    stats = p.stat()

    file_type = (
        'l' if p.is_symlink() else
        'd' if p.is_dir() else
        'f' if p.is_file() else
        '?'
    )

    lines = [
        f"size: {stats.st_size}",
        f"created: {getattr(stats, 'st_birthtime', None)}",
        f"modified: {stats.st_mtime}",
        f"accessed: {stats.st_atime}",
        f"type: {file_type}",
        f"permissions: {oct(stats.st_mode)[-3:]}",
    ]

    return "\n".join(lines)


def fs_read(path: str, start: int = 0, end: int = -1) -> str:
    p = Path(path)
    if not is_inside(p, config.wd): raise PathOutsideWorkDir(path=path, wd=config.wd)
    if not p.exists(): raise PathDoesNotExist(path=path)
    if not p.is_file(): raise PathIsNotFile(path=path)

    with open(p, 'r') as f:
        lines = f.readlines()

    if end == -1:
        sliced = lines[start:]
    elif end < -1:
        sliced = lines[start:len(lines) + 1 + end]
    else:
        sliced = lines[start:end + 1]

    return "".join(sliced)


def fs_write(path: str, content: str, mode: str = 'w') -> str:
    p = Path(path)
    if not is_inside(p, config.wd): raise PathOutsideWorkDir(path=path, wd=config.wd)

    with open(p, mode) as f:
        f.write(content)

    return f"Successfully wrote {len(content)} characters to {path} (mode: {mode})"


def fs_list(path: str = ".") -> str:
    p = Path(path)
    if not is_inside(p, config.wd): raise PathOutsideWorkDir(path=path, wd=config.wd)
    if not p.exists(): raise PathDoesNotExist(path=path)
    if not p.is_dir(): raise PathIsNotDirectory(path=path)

    entries = []
    for item in sorted(p.iterdir(), key=lambda x: x.name):
        try:
            stats = item.stat()
        except:
            continue # could be a broken symlink or a restricted file, for example

        size = stats.st_size

        file_type = (
            'l' if item.is_symlink() else
            'd' if item.is_dir() else
            'f' if item.is_file() else
            '?'
        )

        entries.append((size, file_type, item.name))

    if not entries:
        return ""

    lines = [
        f"{str(size).rjust(12)}  {file_type}  {name.ljust(50)}"
        for size, file_type, name in entries
    ]

    return "\n".join(lines)


def fs_search(path: str, pattern: str) -> str:
    p = Path(path)
    if not is_inside(p, config.wd): raise PathOutsideWorkDir(path=path, wd=config.wd)
    if not p.exists(): raise PathDoesNotExist(path=path)

    result = subprocess.run(
        ["rg", "--line-number", "--color", "never", pattern, str(p)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return result.stdout
    elif result.returncode == 1:
        return ""  # No matches found
    else:
        return f"Error: {result.stderr}"


def fs_rm(path: str) -> str:
    p = Path(path)
    if not is_inside(p, config.wd): raise PathOutsideWorkDir(path=path, wd=config.wd)
    if not p.exists(): raise PathDoesNotExist(path=path)

    if p.is_dir():
        # Require confirmation for directory deletion
        print(f"\nDelete directory '{path}' and all its contents?", file=sys.stderr)
        print("  [Y] Yes | [N] No", file=sys.stderr)

        response = input("> ").strip().upper()

        if response != 'Y':
            raise CommandDenied(command=f"rm {path}")

        # Recursively delete directory
        import shutil
        shutil.rmtree(p)
        return f"Successfully deleted directory {path} and all its contents"

    else:
        # Delete file without confirmation
        p.unlink()
        return f"Successfully deleted file {path}"


def fs_mkdir(path: str) -> str:
    p = Path(path)
    if not is_inside(p, config.wd): raise PathOutsideWorkDir(path=path, wd=config.wd)
    if p.exists(): raise PathAlreadyExists(path=path)

    p.mkdir(parents=True, exist_ok=False)

    return f"Successfully created directory at {path}"


def fs_replace(path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
    try:
        with open(path) as f:
            content = f.read()
    except Exception as e:
        raise FailedReplace(f"Error reading file: {str(e)}")

    if len(old_string) == 0:
        raise FailedReplace("old_string must be a non-empty string")

    if old_string == new_string:
        raise FailedReplace("new_string must be different from old_string")

    count = content.count(old_string)

    if count == 0:
        raise FailedReplace("old_string not found in content")

    if replace_all:
        updated_content = content.replace(old_string, new_string)
    else:
        updated_content = content.replace(old_string, new_string, 1)

    try:
        with open(path, 'w') as f:
            f.write(updated_content)
    except Exception as e:
        raise FailedReplace(f"Error writing file: {str(e)}")

    return f"Made {count if replace_all else 1} replacements"


def is_inside(path, root):
    try:
        Path(path).absolute().relative_to(Path(root).absolute())
        Path(path).resolve().relative_to(Path(root).resolve())
  
        return True
  
    except (ValueError, RuntimeError, OSError):
        return False
