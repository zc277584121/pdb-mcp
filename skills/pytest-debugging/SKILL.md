---
name: Pytest Debugging Best Practices
description: This skill should be used when the user asks to "debug a failing test", "debug pytest", "use pytest with pdb", "fix a test failure", "debug test assertions", "start pytest debug session", or mentions debugging Python tests with pytest. Provides structured workflows for debugging test failures using pdb-mcp's pytest integration.
version: 0.1.0
---

# Pytest Debugging Best Practices

## Purpose

Provide structured workflows for debugging Python test failures using pdb-mcp's `start_pytest_debug` tool. Enable efficient investigation of test failures by choosing the right debugging mode and following systematic investigation patterns.

## Core Principle: Understand the Failure First

Before starting a pytest debug session:

1. **Read the test failure output** - Understand what assertion failed and why
2. **Read the test code** - Understand what the test expects
3. **Read the code under test** - Understand what the code actually does
4. **Choose the right debugging mode** based on the failure type

## Choosing the Right Debug Mode

### Mode 1: `--pdb` (Break on Failure) — Default

Use when a test fails and investigation is needed at the point of failure.

```json
{
  "args": "tests/test_module.py -x",
  "python_path": ".venv/bin/python",
  "working_directory": "/project"
}
```

**Behavior**: Runs all tests normally. When a test fails, drops into pdb at the assertion failure point. The `-x` flag stops at first failure.

**Best for**:
- Assertion failures where the state at failure time matters
- Understanding why an actual value differs from expected
- Errors that occur during test execution

### Mode 2: `--trace` (Break at Test Start)

Use when stepping through the test from the beginning is needed.

```json
{
  "args": "tests/test_module.py::test_specific_function",
  "python_path": ".venv/bin/python",
  "working_directory": "/project",
  "stop_at_start": true
}
```

**Behavior**: Enters pdb before the first test starts. Allows setting breakpoints and stepping through from the beginning.

**Best for**:
- Understanding the test's execution flow
- Bugs where the failure location doesn't reveal the root cause
- Investigating test setup/teardown issues

### Decision Guide

| Situation | Mode | Reason |
|-----------|------|--------|
| AssertionError with unclear values | `--pdb` | Inspect values at failure point |
| Test passes but shouldn't | `--trace` | Step through to find why |
| Error in fixture/setup | `--pdb` | Drops into pdb at the error |
| Need to trace data flow | `--trace` | Set breakpoints along the path |
| Intermittent failure | `--pdb` with `-x` | Catch it when it happens |
| Debugging test logic itself | `--trace` | Step through test code |

## Debugging Workflows

### Workflow 1: Assertion Failure Investigation

The most common scenario - a test assertion fails.

1. **Read the failure output** to get:
   - Which assertion failed
   - The actual vs expected values
   - The line number

2. **Start pytest debug session** (default `--pdb` mode):
   ```json
   {
     "args": "tests/test_module.py::test_failing -x",
     "python_path": ".venv/bin/python",
     "working_directory": "/project"
   }
   ```

3. **When pdb activates at the failure**:
   ```
   l           # See code around the assertion
   p actual    # Print the actual value
   p expected  # Print the expected value
   ```

4. **Navigate up the call stack** to find where things went wrong:
   ```
   w           # Show call stack
   u           # Move to the function under test
   p locals()  # Check the function's state
   ```

5. **Trace back to the root cause**:
   ```
   u           # Keep going up if needed
   a           # Check function arguments
   p self.attribute  # Check object state
   ```

### Workflow 2: Debugging Code Under Test

When the root cause is in the application code, not the test.

1. **Start with `--trace` mode** to break before execution:
   ```json
   {
     "args": "tests/test_module.py::test_specific -x",
     "python_path": ".venv/bin/python",
     "working_directory": "/project",
     "stop_at_start": true
   }
   ```

2. **Set breakpoints in application code**:
   ```
   b src/module.py:42     # Break in the function being tested
   b src/utils.py:15      # Break in helper functions
   c                       # Continue to first breakpoint
   ```

3. **Step through application logic**:
   ```
   a           # Check function inputs
   n           # Step through
   p result    # Check intermediate values
   ```

### Workflow 3: Debugging Fixtures and Setup

When the issue is in test fixtures, setup, or teardown.

1. **Start with `--trace` mode**:
   ```json
   {
     "args": "tests/test_module.py::test_with_fixture -x",
     "python_path": ".venv/bin/python",
     "working_directory": "/project",
     "stop_at_start": true
   }
   ```

2. **Set breakpoints in fixture code**:
   ```
   b conftest.py:20       # Break in fixture
   c
   ```

3. **Inspect fixture values**:
   ```
   p fixture_value
   n                      # Step through fixture setup
   ```

## Pytest-Specific Args Patterns

### Selecting Tests to Debug

```
"args": "tests/"                              # All tests
"args": "tests/test_module.py"                # One file
"args": "tests/test_module.py::test_func"     # One test
"args": "tests/test_module.py::TestClass"     # One class
"args": "tests/test_module.py::TestClass::test_method"  # One method
"args": "-k 'test_login or test_auth'"        # By name pattern
"args": "-k 'not slow'"                       # Exclude by pattern
"args": "-m 'unit'"                           # By marker
```

### Useful Flag Combinations

```
"args": "tests/ -x"                    # Stop at first failure
"args": "tests/ -x -v"                 # Verbose + stop at first failure
"args": "tests/ --lf"                  # Re-run only last failed tests
"args": "tests/ --ff"                  # Run failed tests first
"args": "tests/ -x --tb=long"         # Detailed traceback
"args": "tests/ -x --tb=short"        # Compact traceback
```

## Timeout Considerations

Pytest sessions often need longer timeouts:

- **Default (10.0s)**: Suitable for small test suites
- **Large test suites**: Set `timeout: 30` or higher for suites with many tests or slow setup
- **Tests with I/O**: Tests involving database, network, or file operations may need longer timeouts
- **Collection phase**: If pytest takes a long time to discover tests, increase timeout

## Common Mistakes to Avoid

1. **Debugging all tests at once** - Always narrow down to the specific failing test with `-x` and test selection
2. **Using `--trace` when `--pdb` suffices** - `--trace` means stepping from the beginning; `--pdb` jumps directly to the failure
3. **Forgetting `-x` flag** - Without `-x`, pytest continues to the next test after pdb exits, which is rarely desired during debugging
4. **Not reading failure output first** - The pytest failure output often contains enough info to form a hypothesis before debugging
5. **Debugging in the test when the bug is in app code** - Set breakpoints in application code, not just in the test file

## Additional Resources

### Reference Files

For detailed pytest debugging patterns and techniques:
- **`references/pytest-debug-patterns.md`** - Advanced patterns for common pytest debugging scenarios
