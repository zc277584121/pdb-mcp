---
name: PDB Debugging Best Practices
description: This skill should be used when the user asks to "debug a Python script", "start a pdb session", "set breakpoints", "step through code", "inspect variables in pdb", "use pdb-mcp to debug", or mentions debugging Python code with pdb. Provides structured debugging workflows and best practices for the pdb-mcp MCP server.
version: 0.1.0
---

# PDB Debugging Best Practices

## Purpose

Provide structured workflows and best practices for debugging Python scripts using the pdb-mcp MCP server. Follow these guidelines to conduct efficient, methodical debugging sessions instead of randomly stepping through code.

## Core Principle: Analyze First, Debug Second

**Never start a debug session blindly.** Before calling `start_debug`, always:

1. Read and understand the relevant source code
2. Identify suspicious locations based on the error or unexpected behavior
3. Plan breakpoints at strategic locations
4. Only then start the debug session with a clear investigation plan

## Debugging Workflow

### Step 1: Analyze the Problem

Before touching the debugger, gather context:

- Read the error message or traceback carefully
- Read the source code of the failing function and its callers
- Form a hypothesis about what might be wrong
- Identify 1-3 key locations to investigate

### Step 2: Plan Breakpoints Strategically

Choose breakpoint locations based on the hypothesis:

| Scenario | Where to Set Breakpoints |
|----------|-------------------------|
| Wrong return value | Before the return statement |
| Exception raised | At the line in the traceback |
| Wrong variable value | Where the variable is first assigned or modified |
| Logic error in loop | At the loop entry and inside the loop body |
| Function called with wrong args | At the function entry point |
| Data transformation bug | Before and after the transformation |

### Step 3: Start the Debug Session

Call `start_debug` with the correct parameters:

- **script_path**: Path to the script to debug (relative to working_directory)
- **python_path**: The project's Python interpreter (typically `.venv/bin/python`)
- **working_directory**: The project root directory
- **env**: Any needed environment variables

### Step 4: Set Breakpoints Before Running

Immediately after starting, set breakpoints at planned locations **before** continuing execution:

```
b 42              # Break at line 42 of current file
b utils.py:15     # Break at line 15 of utils.py
b my_function     # Break when my_function is called
```

Then continue execution with `c` to run to the first breakpoint.

### Step 5: Investigate at Breakpoints

At each breakpoint, follow this investigation pattern:

1. **Orient** - `l` to see surrounding code, `w` to see the call stack
2. **Inspect** - `p variable` to check values, `a` to see function arguments
3. **Evaluate** - `!expression` to test hypotheses
4. **Decide** - Continue (`c`), step into (`s`), step over (`n`), or return (`r`)

### Step 6: Conclude and Fix

After identifying the root cause:

1. Quit the debugger with `q`
2. Apply the fix to the source code
3. Re-run to verify the fix works

## Common Debugging Patterns

### Pattern: Tracing a Variable's Value

To track how a variable changes through execution:

```
b <first_assignment_line>
c
p variable_name
n                    # Step through, checking value after each step
p variable_name
```

### Pattern: Finding Where an Exception Occurs

When the traceback points to a specific line:

```
b <traceback_line - 2>    # Break a few lines before the crash
c
p relevant_variables       # Check state just before the crash
n                          # Step to see exactly where it fails
```

### Pattern: Investigating a Function Call

To understand what a function receives and returns:

```
b function_name
c
a                    # Print all arguments
n / s               # Step through the function
p result            # Check return value before return
```

### Pattern: Conditional Investigation

When a bug only happens with certain data:

```
b 50                # Set breakpoint
c
p data              # Check if this is the interesting case
c                   # If not, continue to next hit
```

For frequent breakpoint hits, consider using pdb conditional breakpoints:
```
b 50, len(data) > 100    # Only break when condition is true
```

## Key pdb Commands Reference

### Execution Control

| Command | Purpose |
|---------|---------|
| `n` | Next line (step over function calls) |
| `s` | Step into function calls |
| `c` | Continue to next breakpoint |
| `r` | Run until current function returns |
| `until <line>` | Continue until reaching a line number > current |
| `j <line>` | Jump to line (skip or re-execute code) |

### Breakpoint Management

| Command | Purpose |
|---------|---------|
| `b <line>` | Set breakpoint at line |
| `b <file>:<line>` | Set breakpoint in another file |
| `b <func>` | Set breakpoint at function entry |
| `b <line>, <cond>` | Conditional breakpoint |
| `tbreak <line>` | Temporary breakpoint (auto-clears after hit) |
| `cl <num>` | Clear breakpoint by number |
| `disable/enable <num>` | Toggle breakpoint |

### Inspection

| Command | Purpose |
|---------|---------|
| `l` | List code around current line |
| `ll` | List entire current function |
| `w` | Show call stack (where) |
| `u` / `d` | Move up/down the call stack |
| `p <expr>` | Print expression value |
| `pp <expr>` | Pretty-print expression |
| `a` | Print function arguments |
| `!<stmt>` | Execute Python statement |

## Timeout Considerations

The pdb-mcp server uses smart output waiting. Adjust timeout when needed:

- **Default (5.0s)**: Fine for most commands
- **Increase for slow operations**: Scripts that do network calls, heavy computation, or large file I/O may need `timeout: 15` or higher
- **The timeout is idle-based**: As long as output keeps flowing, the server keeps waiting. The timeout only triggers when output stops.

## Common Mistakes to Avoid

1. **Starting debug without reading code first** - Always read the source before debugging
2. **Stepping line-by-line from the start** - Set breakpoints at strategic points, then `c` to jump there
3. **Forgetting to set breakpoints before `c`** - After `start_debug`, set breakpoints immediately, then continue
4. **Not checking the call stack** - Use `w` to understand the full context, not just the current line
5. **Ignoring function arguments** - Use `a` to verify functions receive expected inputs
6. **Not using conditional breakpoints** - For loops or frequent calls, use `b <line>, <condition>` to avoid manual checking

## Additional Resources

### Reference Files

For detailed debugging workflows and advanced techniques:
- **`references/debugging-workflows.md`** - Step-by-step workflows for common debugging scenarios
- **`references/pdb-commands-cheatsheet.md`** - Complete pdb command reference with examples
