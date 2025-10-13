"""Essentials MCP server with filesystem, shell, and web tools."""

import types as _types

from .fs import (
    fs_pwd,
    fs_stat,
    fs_read,
    fs_write,
    fs_list,
    fs_search,
    fs_replace,
    fs_mkdir,
    fs_rm,
)

from .shell import (
    shell_run,
)

from .web import (
    web_search,
    web_fetch,
)

from .utils import (
    ToolError,
    PathDoesNotExist,
    PathIsNotDirectory,
    PathIsNotFile,
    PathOutsideWorkDir,
    PathAlreadyExists,
    InvalidUrl,
    MissingOrEmpty,
    CommandDenied,
    CommandForbidden,
    FailedReplace,
    UnsupportedMimeType,
    ResponseTooLong,
    RequestFailed,
)


__all__ = [
    name for name, obj in globals().items()
    if not name.startswith('_') and not isinstance(obj, _types.ModuleType)
]

