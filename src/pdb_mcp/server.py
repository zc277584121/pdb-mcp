"""MCP server implementation for PDB debugging"""

from mcp.server import Server
from mcp.types import Tool, TextContent

from .session import PdbSession


# Global session instance
pdb_session = PdbSession()

# Create MCP server
app = Server("pdb-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available pdb debugging tools"""
    return [
        Tool(
            name="start_debug",
            description="Start a Python debugging session using pdb. This will launch the Python debugger for the specified script.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Path to the Python script to debug (e.g., 'script.py' or '/path/to/script.py')",
                    },
                    "args": {
                        "type": "string",
                        "description": "Optional command-line arguments to pass to the script",
                        "default": "",
                    },
                    "python_path": {
                        "type": "string",
                        "description": "Path to Python interpreter for the project or script being debugged. The agent typically knows the project's Python interpreter path. If not provided, use 'python' as fallback",
                        "default": "",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Time to wait without new output before returning (seconds). Returns immediately when pdb prompt is detected. Default: 5.0",
                        "default": 5.0,
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Directory to run the command in. Defaults to current directory. The agent typically knows the project directory.",
                        "default": "",
                    },
                    "env": {
                        "type": "object",
                        "description": "Optional environment variables to set for the debugging session (e.g., {'DEBUG': '1', 'API_KEY': 'test'}). These will be added to the existing environment.",
                        "default": {},
                    },
                },
                "required": ["script_path", "python_path", "working_directory"],
            },
        ),
        Tool(
            name="start_pytest_debug",
            description="Start a pytest debugging session using 'pytest --pdb'. When test failures occur, pytest will automatically enter pdb for interactive debugging. Use args to control when and how failures trigger debugging (e.g., '-x' for first failure only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "args": {
                        "type": "string",
                        "description": """Arguments to pass after 'pytest --pdb'. Common usage patterns:

Test Selection:
- 'test_module.py' - Run specific file
- 'test_module.py::test_function' - Run specific test function
- 'test_module.py::TestClass::test_method' - Run specific test method
- 'tests/' - Run all tests in directory

Filtering:
- '-k test_login' - Run tests matching keyword 'test_login'
- '-m slow' - Run tests with marker 'slow'
- '-x' - Stop at first failure (useful with --pdb)
- '--maxfail=3' - Stop after 3 failures

Output Control:
- '-v' - Verbose output with test names
- '-s' - Show print() output (disable capture)
- '--tb=short' - Short traceback format
- '-q' - Quiet output

Re-run Failed:
- '--lf' - Run only last failed tests
- '--ff' - Run failed tests first, then others

Combined Examples:
- '-x test_auth.py' - Stop at first failure in test_auth.py
- '-v -k login tests/' - Verbose, run login tests in tests/ directory
- '-x -s test_api.py::test_post' - Stop at first failure, show prints, run specific test
- '--lf -v' - Re-run last failed tests with verbose output

Leave empty to run all tests in current directory.""",
                        "default": "",
                    },
                    "python_path": {
                        "type": "string",
                        "description": "Path to Python interpreter for the project or script being debugged. The agent typically knows the project's Python interpreter path. If not provided, use 'python' as fallback",
                        "default": "",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Time to wait without new output before returning (seconds). Returns immediately when pdb prompt is detected. Default: 10.0",
                        "default": 10.0,
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Directory to run the command in. Defaults to current directory. The agent typically knows the project directory.",
                        "default": "",
                    },
                    "env": {
                        "type": "object",
                        "description": "Optional environment variables to set for the debugging session (e.g., {'DEBUG': '1', 'API_KEY': 'test'}). These will be added to the existing environment.",
                        "default": {},
                    },
                },
                "required": ["args", "python_path", "working_directory"],
            },
        ),
        Tool(
            name="execute_pdb_command",
            description="""Execute a pdb command in the active debugging session. 
            
Available commands:

Execution Control:
- n (next): Execute next line (don't step into functions)
- s (step): Execute next line (step into functions)
- c (continue): Continue execution until next breakpoint
- r (return): Execute until current function returns
- until <line>: Continue until line number greater than current (e.g., 'until 15')
- j <line> (jump): Jump to line number (e.g., 'j 10')
- run/restart: Restart the program
- q (quit): Quit debugging session

Breakpoints:
- b <line>: Set breakpoint at line number (e.g., 'b 10')
- b <file>:<line>: Set breakpoint in another file (e.g., 'b utils.py:5')
- b <function>: Set breakpoint at function (e.g., 'b my_function')
- tbreak <line>: Set temporary breakpoint (removed after first hit)
- cl <breakpoint>: Clear breakpoint (e.g., 'cl 1')
- cl: Clear all breakpoints
- disable <breakpoint>: Disable breakpoint (e.g., 'disable 1')
- enable <breakpoint>: Enable breakpoint (e.g., 'enable 1')
- condition <breakpoint> <expr>: Set condition for breakpoint (e.g., 'condition 1 x > 5')
- ignore <breakpoint> <count>: Ignore breakpoint for count times (e.g., 'ignore 1 10')
- commands <breakpoint>: Set commands to execute when breakpoint hits

Code Inspection:
- l (list): Show code around current line
- ll (longlist): Show full source code of current function
- w (where): Show call stack
- u (up): Move up in call stack
- d (down): Move down in call stack
- a (args): Print arguments of current function
- whatis <expr>: Show type of expression (e.g., 'whatis x')

Variables:
- p <expr>: Print expression value (e.g., 'p user_name')
- pp <expr>: Pretty-print expression value
- display <expr>: Auto-display expression when execution stops
- undisplay <number>: Remove auto-display
- ! <statement>: Execute Python statement (e.g., '! x = 10')

Other:
- h (help): Show help for all commands
- h <command>: Show help for specific command (e.g., 'h b')
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The pdb command to execute (e.g., 'n', 's', 'l', 'p variable_name', 'c', etc.)",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Time to wait without new output before returning (seconds). Returns immediately when pdb prompt is detected. Default: 5.0",
                        "default": 5.0,
                    },
                },
                "required": ["command"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    if name == "start_debug":
        script_path = arguments["script_path"]
        args = arguments.get("args", "")
        python_path = arguments.get("python_path") or None
        timeout = arguments.get("timeout", 5.0)
        working_directory = arguments.get("working_directory") or None
        env = arguments.get("env") or None
        result = pdb_session.start(
            script_path, args, python_path, timeout, working_directory, env
        )
        return [TextContent(type="text", text=result)]

    elif name == "start_pytest_debug":
        args = arguments.get("args", "")
        python_path = arguments.get("python_path") or None
        timeout = arguments.get("timeout", 10.0)
        working_directory = arguments.get("working_directory") or None
        env = arguments.get("env") or None
        result = pdb_session.start_pytest(
            args, python_path, timeout, working_directory, env
        )
        return [TextContent(type="text", text=result)]

    elif name == "execute_pdb_command":
        command = arguments["command"]
        timeout = arguments.get("timeout", 5.0)
        result = pdb_session.execute_command(command, timeout)
        return [TextContent(type="text", text=result)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


def get_app():
    """Get the MCP server app instance"""
    return app


def get_session():
    """Get the global PDB session instance"""
    return pdb_session
