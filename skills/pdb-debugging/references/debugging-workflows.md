# Debugging Workflows

Detailed step-by-step workflows for common Python debugging scenarios using pdb-mcp.

## Workflow 1: Debugging a Script That Crashes with an Exception

**Scenario**: A Python script raises an unhandled exception.

### Steps

1. **Read the traceback** to identify the file, line number, and exception type
2. **Read the source code** around the failing line (at least 10 lines of context)
3. **Identify variables** involved in the failing expression
4. **Start debug session**:
   ```
   start_debug(script_path="failing_script.py", python_path=".venv/bin/python", working_directory="/project")
   ```
5. **Set breakpoint 2-3 lines before the crash**:
   ```
   b <crash_line - 3>
   ```
6. **Continue to breakpoint**:
   ```
   c
   ```
7. **Inspect all relevant variables**:
   ```
   p variable1
   p variable2
   pp complex_data_structure
   ```
8. **Step forward line by line** to watch the state change:
   ```
   n
   p variable1    # Check after each step
   ```
9. **Identify the root cause** and quit:
   ```
   q
   ```

### Common Root Causes
- `None` value where an object was expected (missing return, failed lookup)
- Wrong type (string where int expected, list where dict expected)
- Index/key error (off-by-one, missing key in dict)
- Stale or uninitialized variable

---

## Workflow 2: Debugging a Function That Returns Wrong Results

**Scenario**: A function runs without error but returns incorrect output.

### Steps

1. **Determine the expected vs actual output**
2. **Read the function source code** and trace the logic mentally
3. **Identify the data flow**: input → transformations → output
4. **Start debug session** and set breakpoint at function entry:
   ```
   b function_name
   c
   ```
5. **Verify inputs are correct**:
   ```
   a          # Print all arguments
   ```
6. **Step through the function** checking intermediate values:
   ```
   n
   p intermediate_result
   n
   p another_value
   ```
7. **Compare actual vs expected** at each transformation step
8. **Find the divergence point** where actual != expected

### Tips
- Work backwards from the return value when the function is long
- Use `r` to run to return, then check the return value
- Set breakpoints at each major transformation instead of stepping through everything

---

## Workflow 3: Debugging a Loop Issue

**Scenario**: A loop produces wrong results, runs too many/few times, or hangs.

### Steps

1. **Read the loop code** and understand the expected iteration pattern
2. **Start debug session** and set breakpoint at loop entry:
   ```
   b <loop_line>
   c
   ```
3. **Check initial conditions**:
   ```
   p loop_variable
   p collection_being_iterated
   p len(collection)
   ```
4. **Step through first few iterations**:
   ```
   n    # Step through loop body
   p loop_variable    # Check at each iteration
   ```
5. **For long loops**, use conditional breakpoints:
   ```
   b <line>, i == 50       # Break only on iteration 50
   b <line>, item == "target"   # Break on specific value
   ```
6. **Check the exit condition**:
   ```
   p exit_condition_variable
   ```

### Tips
- For infinite loops: set a breakpoint inside the loop and check why the exit condition is never met
- For off-by-one: check the first and last iterations carefully
- Use `until <line>` to skip to end of loop body quickly

---

## Workflow 4: Debugging Import or Initialization Errors

**Scenario**: Script fails during import or module initialization.

### Steps

1. **Read the traceback** - import errors often chain through multiple files
2. **Start debug session** - pdb starts at the first line:
   ```
   start_debug(script_path="script.py", ...)
   ```
3. **Step into imports** using `s` (step) instead of `n` (next):
   ```
   s    # Step into the import statement
   ```
4. **Navigate to the failing module**:
   ```
   s    # Keep stepping into imports
   w    # Check where you are in the import chain
   ```
5. **Set breakpoint at the failing line** once located:
   ```
   b failing_module.py:42
   c
   ```

### Tips
- `n` skips over imports; use `s` to debug import-time code
- Environment variables and paths are common causes - check with `!import os; print(os.environ.get('KEY'))`
- Circular imports: use `w` to see the full import chain

---

## Workflow 5: Debugging Multi-File Issues

**Scenario**: Bug involves interaction between multiple modules.

### Steps

1. **Map the call chain** - read code to understand which files are involved
2. **Set breakpoints across files**:
   ```
   b module_a.py:30
   b module_b.py:15
   b module_c.py:42
   ```
3. **Continue between breakpoints**:
   ```
   c    # Jump to next breakpoint
   ```
4. **At each breakpoint, check the data being passed**:
   ```
   a    # Function arguments (what was received)
   p result    # What will be returned/passed forward
   ```
5. **Use the call stack** to understand context:
   ```
   w    # Show full call stack
   u    # Move up to caller
   p local_var    # Check caller's state
   d    # Move back down
   ```

### Tips
- Set breakpoints at function entry and exit in each module
- Focus on data crossing module boundaries
- Use `u` (up) and `d` (down) to navigate the call stack without continuing execution

---

## Workflow 6: Debugging with Environment Variables

**Scenario**: Bug depends on environment configuration.

### Steps

1. **Start debug with specific env vars**:
   ```json
   {
     "script_path": "app.py",
     "python_path": ".venv/bin/python",
     "working_directory": "/project",
     "env": {
       "DATABASE_URL": "sqlite:///test.db",
       "DEBUG": "1",
       "LOG_LEVEL": "DEBUG"
     }
   }
   ```
2. **Verify environment inside debugger**:
   ```
   !import os; print(os.environ.get('DATABASE_URL'))
   ```
3. **Continue debugging as normal**

### Tips
- Set env vars that enable verbose logging
- Use env vars to switch to test configurations
- Check if the issue is environment-specific by comparing different env settings

---

## Workflow 7: Debugging Data Processing Pipelines

**Scenario**: Data goes through multiple transformation steps and comes out wrong.

### Steps

1. **Identify the pipeline stages** by reading the code
2. **Set breakpoints between each stage**:
   ```
   b 10    # After stage 1
   b 25    # After stage 2
   b 40    # After stage 3
   ```
3. **At each stage, snapshot the data**:
   ```
   pp data    # Pretty-print to see structure
   p len(data)
   p type(data)
   ```
4. **Compare snapshots** to find where data goes wrong
5. **Zoom into the broken stage** with more breakpoints

### Tips
- Use `pp` (pretty-print) for complex data structures
- Check data types at each stage, not just values
- Watch for mutations - use `p id(obj)` to track object identity
