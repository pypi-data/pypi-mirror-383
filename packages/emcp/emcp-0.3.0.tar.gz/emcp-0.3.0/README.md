# `emcp`

Essentials MCP server with tools for filesystem operations, shell execution, and web search.


## Installation

To integrate `emcp`, add it to your MCP configuration file. Minimal setup with `uvx`:

```jsonc
{
  "command": "uvx",
  "args": [
    "emcp"
  ],
  "env": {}
}
```

You can also run it standalone with `uvx` or install the package from PyPI with `uv`:

```bash
uvx emcp
```

```bash
uv tool install emcp
```

### Requirements

- [`rg`](https://github.com/BurntSushi/ripgrep) (ripgrep) in your `PATH` for file search.


## Configuration

You can configure `emcp` through environment variables:

- `EMCP_WORKING_DIRECTORY`: the directory EMCP will restrict file operations to. Defaults to CwD.


## Usage

With `emcp`, the agent has access to a variety of file-system, shell and web tools.

### File System

All filesystem operations are restricted to the configured working directory.

- **fs_pwd**: Get the current working directory
- **fs_stat**: Get file/directory metadata (size, times, type, permissions)
- **fs_list**: List directory contents with size, type, and name
- **fs_read**: Read file contents with optional line ranges
- **fs_write**: Write content to a file using specified mode (w, a, etc.)
- **fs_search**: Search files by regex pattern using ripgrep
- **fs_replace**: Replace occurrences of a string in a file (precise edits)
- **fs_mkdir**: Create directories recursively
- **fs_rm**: Remove files or directories (with user confirmation for directories)

### Shell

- **shell_run**: Execute shell commands with an interactive permission system

On first use of a command, the user is prompted to allow/deny/always allow/never allow it.

### Web

- **web_search**: Search the web using DuckDuckGo


## Sandboxing

While `emcp` enforces _some_ restrictions, it's always safer to run MCP servers in sandboxed environments. Consider using one of:

- Containers, such as docker with a mounted external directory.
- (MacOS-only) `sandbox-exec`, with a profile that restricts file-system access.


## Development

Get the code:

```bash
git clone git@github.com:slezica/emcp.git
```

Run from source:

```bash
cd emcp
uv run emcp
```

Run tests:

```bash
cd emcp
uv run pytest
```

## License

None. Code is knowledge. Use it for good.
