# PDB MCP Server

[![PyPI version](https://badge.fury.io/py/pdb-mcp.svg)](https://badge.fury.io/py/pdb-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for Python debugging using pdb. This allows you to debug Python scripts through MCP tools.

## Features

- **Start Debug Session**: Launch a Python script in debug mode using pdb
- **Start Pytest Debug Session**: Run pytest with automatic pdb on test failures
- **Execute PDB Commands**: Send commands to control the debugging session
- **Auto-detect Python Interpreter**: Automatically uses virtual environment Python
- **Modular Architecture**: Clean separation of concerns with session and server modules

## Installation

### Install from PyPI

```bash
pip install pdb-mcp
```

### Install with uv (Recommended) ⚡️

[`uvx`](https://docs.astral.sh/uv/concepts/tools/) will automatically install the package and run the command.

```bash
uvx pdb-mcp
```

### Development Installation

```bash
pip install -e .
```

## Usage

### As MCP Server

Run the server:

```bash
pdb-mcp
```

The server exposes three tools:

#### 1. `start_debug`

Start a debugging session for a Python script.

**Parameters:**
- `script_path` (required): Path to the Python script to debug
- `python_path` (required): Path to Python interpreter for the project being debugged
- `working_directory` (required): Directory to run the command in (should be the project directory)
- `args` (optional): Command-line arguments to pass to the script
- `timeout` (optional): Time to wait without new output before returning in seconds (default: 5.0). As long as there's new output, will keep waiting.
- `env` (optional): Environment variables to set for the debugging session (e.g., {"DEBUG": "1"})

**Example:**
```json
{
  "script_path": "test_script.py",
  "python_path": "/path/to/python",
  "working_directory": "/path/to/project",
  "env": {"DEBUG": "1"}
}
```

#### 2. `start_pytest_debug`

Start a pytest debugging session that automatically drops into pdb on test failures.

**Parameters:**
- `args` (required): Arguments to pass after 'pytest --pdb'. Can include test paths, filters, and pytest options (e.g., "tests/test_example.py -v", "-k test_login", "-x test_auth.py")
- `python_path` (required): Path to Python interpreter for the project being debugged
- `working_directory` (required): Directory to run the command in (should be the project directory)
- `timeout` (optional): Time to wait without new output before returning in seconds (default: 10.0). As long as there's new output, will keep waiting.
- `env` (optional): Environment variables to set for the debugging session (e.g., {"DEBUG": "1"})

**Example:**
```json
{
  "args": "tests/test_example.py -v",
  "python_path": "/path/to/python",
  "working_directory": "/path/to/project",
  "env": {"DEBUG": "1"}
}
```

#### 3. `execute_pdb_command`

Execute a pdb command in the active debugging session.

**Parameters:**
- `command` (required): The pdb command to execute
- `timeout` (optional): Time to wait without new output before returning in seconds (default: 5.0)

**Available Commands:**
- `n` (next): Execute next line (don't step into functions)
- `s` (step): Execute next line (step into functions)
- `b <line>`: Set breakpoint at line (e.g., `b 10`)
- `b <file>:<line>`: Set breakpoint in another file (e.g., `b utils.py:5`)
- `l` (list): Show code around current line
- `p <var>`: Print variable value (e.g., `p user_name`)
- `c` (continue): Continue execution until next breakpoint
- `q` (quit): Quit debugging session
- `h` (help): Show help for all commands
- `r` (return): Execute until current function returns
- `w` (where): Show call stack
- `cl <breakpoint>`: Clear breakpoint
- `a` (args): Print arguments of current function

**Example:**
```json
{
  "command": "n"
}
```

## Testing

### Basic Script Debugging

A sample test script is provided: `test_script.py`

Run the automated test:
```bash
uv run python test_mcp_client.py
```

Example debugging workflow:
1. Start debug: `start_debug` with `script_path = "test_script.py"`
2. Step through code: `execute_pdb_command` with `command = "n"`
3. View code: `execute_pdb_command` with `command = "l"`
4. Print variable: `execute_pdb_command` with `command = "p num"`
5. Continue: `execute_pdb_command` with `command = "c"`
6. Quit: `execute_pdb_command` with `command = "q"`

### Pytest Debugging

A sample test file is provided: `test_example.py`

Run the pytest debugging test:
```bash
uv run python test_pytest_client.py
```

The test will:
1. Run pytest with `-x --pdb` flags
2. Stop at the first failing test
3. Drop into pdb at the assertion failure
4. Allow you to inspect variables and debug

## Configuration

To use with Claude Desktop or other MCP clients, add to your configuration file (e.g., `claude_desktop_config.json`):

### Using uvx (Recommended)

```json
{
  "mcpServers": {
    "pdb-debugger": {
      "command": "uvx",
      "args": ["--from", "pdb-mcp", "pdb-mcp"]
    }
  }
}
```

### Using Local Development Version

```json
{
  "mcpServers": {
    "pdb-debugger": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/pdb-mcp",
        "run",
        "pdb-mcp"
      ]
    }
  }
}
```

Replace `/path/to/pdb-mcp` with the actual path to this project.

## Architecture

### Project Structure

```
src/pdb_mcp/
├── __init__.py      # Entry point and main function
├── session.py       # PdbSession class for managing pdb processes
└── server.py        # MCP server and tool definitions
```

### Session Management

The `PdbSession` class maintains a persistent pdb process:
- Uses `subprocess.Popen` to launch pdb with the target script
- Communicates via stdin/stdout pipes
- Background thread reads output asynchronously
- Maintains debugging session state between command executions
- Auto-detects Python interpreter from virtual environment

### Python Interpreter Configuration

The `python_path` parameter specifies the Python interpreter for the **client's project** (not the server's environment):

- **Required parameter**: Agents should provide the project's Python interpreter path
- **Typical values**: 
  - `.venv/bin/python` or `venv/bin/python` for virtual environments
  - `/usr/bin/python3` for system Python
  - Custom paths for conda or other environments
- **Fallback**: If not provided or empty, falls back to `"python"` command (uses system PATH)

**Note:** The server does NOT use its own Python (`sys.executable`) because the MCP server may run in a different environment than the client's project being debugged.

### Working Directory Configuration

Both `start_debug` and `start_pytest_debug` require a `working_directory` parameter:

- **Required parameter**: Should be the project's root directory or the directory containing the script
- **Purpose**: Ensures the script runs in the correct directory context
- **Use cases**:
  - Scripts that use relative file paths
  - Projects with specific directory structure requirements
  - Loading configuration files from project root
- **Agent integration**: Agents (like Claude) typically know the project directory and should provide it

**Example:**
```json
{
  "script_path": "src/main.py",
  "working_directory": "/home/user/myproject"
}
```

This is equivalent to running:
```bash
cd /home/user/myproject && python -m pdb src/main.py
```

### Smart Output Waiting

The server uses an intelligent output waiting mechanism:

- **Single timeout parameter**: Time to wait without new output before returning
- **No total time limit**: As long as there's new output, the server keeps waiting
- **Adaptive**: Fast commands return quickly, slow commands get as much time as they need
- **User configurable**: All tools accept a `timeout` parameter

**How it works:**
1. Server continuously checks for output every 0.1 seconds
2. Each time new output arrives, the idle timer resets
3. When there's no new output for `timeout` seconds, it returns
4. No matter how long the script runs, if it keeps producing output, the server waits

**Default timeout values:**
- `start_debug`: 5.0 seconds (pdb usually starts quickly)
- `start_pytest_debug`: 10.0 seconds (tests may produce output slowly)
- `execute_pdb_command`: 5.0 seconds (most commands are quick)

**Example:** A script that runs for 10 seconds but prints every 0.5 seconds will work fine with `timeout=3.0`, because the idle time never exceeds 3 seconds.

## License

See LICENSE file for details.

