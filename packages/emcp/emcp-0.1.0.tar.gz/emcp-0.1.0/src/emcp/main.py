#!/usr/bin/env python3
"""
Essentials MCP server with filesystem, shell, and web tools.
"""

import os
import sys
import signal
import asyncio
import traceback
import textwrap
import subprocess
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent, ErrorData, INTERNAL_ERROR, INVALID_PARAMS
import mcp.server.stdio

from .shell import shell_run
from .fs import (
    fs_list,
    fs_mkdir,
    fs_pwd,
    fs_read,
    fs_replace,
    fs_rm,
    fs_search,
    fs_stat,
    fs_write,
)
from .web import web_search


# --------------------------------------------------------------------------------------------------
# MCP Server

app = Server("ai-tools")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="fs_pwd",
            description="""
                Get the current working directory, where file access is allowed.
                Return the absolute path.
            """,
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="fs_stat",
            description="""
            Get information about a file or directory.
            Returns file attributes including: 
                - size in bytes
                - created time
                - modified time
                - accessed time
                - type ('f' for file, 'd' for directory or 'l' for link)
                - permissions
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file or directory"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="fs_read",
            description="""
            Read lines from a file.
            Accepts arguments to start and end at specified lines. Both indices are inclusive and can be
            negative to count from the end (-1 is the last line).
            Returns the content as read.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file"
                    },
                    "start": {
                        "type": "integer",
                        "description": "The line number to start from (inclusive), defaults to 0",
                        "default": 0
                    },
                    "end": {
                        "type": "integer",
                        "description": "The line number to end at (inclusive), defaults to -1 (last line)",
                        "default": -1
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="fs_write",
            description="""
            Write content to a file using the specified mode.
            Returns a success message.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write"
                    },
                    "mode": {
                        "type": "string",
                        "description": "File mode - 'w' (write/overwrite), 'w+' (write/read), 'a' (append), 'a+' (append/read), etc.",
                        "default": "w"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="fs_list",
            description="""
            List files and directories in the given directory path.
            Returns a table with columns:
                - size (in bytes),
                - type ('f' for file, 'd' for directory or 'l' for link)
                - name
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to list, defaults to current directory",
                        "default": "."
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="fs_search",
            description="""
                Search files for a regex pattern in the provided directory path.
                Returns matching lines in <file>:<line>:<content> format.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to search in"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "The regex pattern to search for"
                    }
                },
                "required": ["path", "pattern"]
            }
        ),
        Tool(
            name="fs_replace",
            description="""
                Replace occurences of a string in a file for a new string.
                Good for precise edits, including changes, insertions and deletions.
                Returns the number of replacements made.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file"
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The string to find and replace"
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The replacement string"
                    },
                    "replace_all": {
                        "type": "boolean",
                        "description": "A boolean indicating whether to replace all occurences (true) or just the first (false)",
                        "default": False
                    }
                },
                "required": ["path", "old_string", "new_string"]
            }
        ),
        Tool(
            name="fs_mkdir",
            description="""
                Create a directory at the given path.
                Creates parent directories as needed (like mkdir -p).
                Returns a success message.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the directory to create"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="fs_rm",
            description="""
                Remove a file or directory at the given path.
                Can be denied by the user.
                For directories, recursively deletes all contents.
                Returns a success message.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file or directory to remove"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="shell_run",
            description="""
                Run a shell command with arguments.
                Can be denied by the user.
                Returns the mixed stdout/stderr output.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    },
                    "arguments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of arguments to pass to the command"
                    }
                },
                "required": ["command", "arguments"]
            }
        ),
        Tool(
            name="web_search",
            description="""
                Fetch a list of web results based on a query.
                Returns a sequence of results with:
                    - index: the position of the match
                    - title: the found website title
                    - url: the found website URL
                    - snippet: a short string that usually shows the query match.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="web_fetch",
            description="""
                Fetch web content from a URL.
                Returns a plain-text representation of the content.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch"
                    }
                },
                "required": ["url"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    try:
        if name == "fs_pwd":
            result = fs_pwd()

        elif name == "fs_stat":
            result = fs_stat(arguments["path"])

        elif name == "fs_read":
            result = fs_read(
                arguments["path"],
                arguments.get("start", 0),
                arguments.get("end", -1)
            )

        elif name == "fs_write":
            result = fs_write(
                arguments["path"],
                arguments["content"],
                arguments.get("mode", "w")
            )

        elif name == "fs_list":
            result = fs_list(arguments.get("path", "."))

        elif name == "fs_search":
            result = fs_search(arguments["path"], arguments["pattern"])

        elif name == "fs_replace":
            result = fs_replace(
                arguments["path"],
                arguments["old_string"],
                arguments["new_string"],
                arguments.get("replace_all", False)
            )

        elif name == "fs_mkdir":
            result = fs_mkdir(arguments["path"])

        elif name == "fs_rm":
            result = fs_rm(arguments["path"])

        elif name == "shell_run":
            result = shell_run(arguments["command"], arguments["arguments"])

        elif name == "web_search":
            result = web_search(arguments["query"])

        # elif name == "web_fetch":
        #     result = web_fetch(arguments["url"])

        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=str(result))]

    except Exception as e:
        traceback.print_exc()
        error_msg = f"Error: {str(e) or repr(e)}"
        return [TextContent(type="text", text=error_msg)]


# --------------------------------------------------------------------------------------------------
# Main

async def async_main():
    loop = asyncio.get_event_loop()
    task = asyncio.current_task()
    assert task

    def signal_handler():
        task.cancel()

    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    try:
        async with mcp.server.stdio.stdio_server() as (rstream, wstream):
            await app.run(rstream, wstream, app.create_initialization_options())

    except asyncio.CancelledError:
        pass


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
