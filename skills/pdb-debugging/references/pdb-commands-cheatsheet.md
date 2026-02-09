# PDB Commands Cheatsheet

Complete reference for all pdb commands available through pdb-mcp's `execute_pdb_command` tool.

## Execution Control

### `n` (next)
Execute the current line and stop at the next line in the **same** function.
- Does NOT step into function calls
- If the current line calls a function, it runs the entire function and stops at the next line

```
> my_script.py(10)main()
-> result = process(data)
(Pdb) n
> my_script.py(11)main()
-> print(result)
```

### `s` (step)
Execute the current line and stop at the **first possible** place (either in a called function or next line).
- Steps INTO function calls
- Use when investigating what happens inside a function

```
> my_script.py(10)main()
-> result = process(data)
(Pdb) s
> my_script.py(1)process()
-> def process(data):
```

### `c` (continue)
Continue execution until the next breakpoint is hit or the program ends.
- Runs at full speed between breakpoints
- Essential for skipping uninteresting code

### `r` (return)
Continue execution until the current function returns.
- Useful when inside a function and want to see its return value
- After return, shows the return value

```
(Pdb) r
--Return--
> my_script.py(15)process()->42
-> return result
```

### `until <line>`
Continue execution until reaching a line number greater than the current line.
- Useful for skipping to end of a loop
- Only works within the current frame

```
(Pdb) until 30    # Continue until line 30 or beyond
```

### `j <line>` (jump)
Jump to a specific line number without executing the lines in between.
- **Dangerous**: Skips code, may cause inconsistent state
- Only works within the current frame
- Useful for re-executing a block or skipping over code

```
(Pdb) j 5    # Jump back to line 5 (re-execute from there)
```

## Breakpoint Management

### `b` (break)

Set a breakpoint. Multiple formats:

```
b 10                    # Break at line 10 of current file
b utils.py:25           # Break at line 25 of utils.py
b my_function           # Break at entry of my_function
b MyClass.method        # Break at entry of MyClass.method
b 10, x > 5            # Conditional: only break when x > 5
b module.func, n == 0   # Conditional on function entry
```

List all breakpoints:
```
b                       # With no arguments, list all breakpoints
```

Output format:
```
Num Type         Disp Enb   Where
1   breakpoint   keep yes   at my_script.py:10
2   breakpoint   keep yes   at utils.py:25
    stop only if x > 5
```

### `tbreak` (temporary break)
Same as `b` but automatically removed after first hit.

```
tbreak 42              # Break at line 42 once, then auto-remove
```

Useful for:
- One-time checks
- Breaking at a specific iteration without lingering breakpoints

### `cl` (clear)
Remove breakpoints:

```
cl 1                   # Clear breakpoint number 1
cl                     # Clear all breakpoints (asks for confirmation)
cl my_script.py:10     # Clear breakpoint at specific location
```

### `disable` / `enable`
Temporarily disable or re-enable breakpoints:

```
disable 1              # Disable breakpoint 1 (still exists, won't trigger)
enable 1               # Re-enable breakpoint 1
```

### `ignore`
Ignore a breakpoint for N crossings:

```
ignore 1 10            # Skip breakpoint 1 the next 10 times
```

### `condition`
Add or change the condition on a breakpoint:

```
condition 1 x > 100    # Add condition to breakpoint 1
condition 1            # Remove condition from breakpoint 1
```

## Code Inspection

### `l` (list)
Show source code around the current line:

```
l                      # Show 11 lines around current position
l 20                   # Show 11 lines around line 20
l 1, 30                # Show lines 1 through 30
l .                    # Show around current position (reset after l)
```

### `ll` (longlist)
Show the entire source code of the current function:

```
ll                     # Full function listing
```

### `w` (where)
Print the call stack trace:

```
w                      # Show full call stack
```

Output: Most recent call is at the bottom. Arrow `>` indicates current frame.

```
  /usr/lib/python3.10/runpy.py(196)_run_module_as_main()
  my_script.py(50)main()
> my_script.py(30)process()
-> result = transform(data)
```

### `u` (up)
Move up one frame in the call stack (to the caller):

```
u                      # Move to caller's frame
p local_var            # Inspect caller's local variables
```

### `d` (down)
Move down one frame in the call stack (to the callee):

```
d                      # Move back to callee's frame
```

## Variable Inspection

### `p` (print)
Evaluate and print an expression:

```
p variable             # Print variable value
p len(my_list)         # Print expression result
p obj.attribute        # Print object attribute
p dict_var['key']      # Print dict value
p [x for x in range(5)]  # Print comprehension result
```

### `pp` (pretty-print)
Pretty-print with formatting (useful for large data structures):

```
pp my_dict             # Formatted dict output
pp list_of_objects     # Formatted list output
```

### `a` (args)
Print all arguments of the current function:

```
(Pdb) a
self = <MyClass instance>
x = 42
y = 'hello'
data = [1, 2, 3]
```

### `display` / `undisplay`
Automatically print expression whenever execution stops:

```
display x              # Show x at every stop
display len(data)      # Show len(data) at every stop
undisplay x            # Stop displaying x
```

### `!` (execute statement)
Execute any Python statement:

```
!x = 42                # Set variable
!import json           # Import module
!print(json.dumps(data, indent=2))  # Format and print
!type(variable)        # Check type
!dir(object)           # List attributes
!isinstance(x, str)    # Type check
```

### `interact`
Start an interactive Python session in the current scope:

```
interact               # Opens Python REPL with current locals
```

Note: Press Ctrl+D to return to pdb.

## Stack Navigation Tips

Combine `w`, `u`, and `d` for powerful stack inspection:

```
w           # See the full call chain
u           # Go up to the caller
p locals()  # See all caller's local variables
u           # Go up another level
a           # See that function's arguments
d           # Go back down
d           # Back to original frame
```

## Advanced Techniques

### Post-mortem Debugging
If a script crashes, pdb enters post-mortem mode at the exception point. All inspection commands work normally to examine the state at the crash site.

### Executing Multi-line Code
Use the `!` prefix for Python statements:

```
!for item in data:
!    print(f"{item.name}: {item.value}")
```

Note: Multi-line may not work well through pdb-mcp. For complex inspection, prefer single expressions:

```
p [(item.name, item.value) for item in data]
```

### Checking Object Details

```
p type(obj)            # Object type
p dir(obj)             # Available attributes/methods
p vars(obj)            # Instance variables
p obj.__dict__         # Same as vars() for most objects
p obj.__class__.__mro__  # Inheritance chain
```
