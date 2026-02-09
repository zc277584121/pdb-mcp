# Pytest Debug Patterns

Advanced patterns and techniques for debugging Python tests with pdb-mcp.

## Pattern 1: Debugging Parameterized Tests

**Scenario**: A parameterized test fails for specific parameter combinations.

### Identify the Failing Parameters

Read the failure output first - pytest shows which parameter set failed:
```
FAILED tests/test_calc.py::test_divide[10-0] - ZeroDivisionError
```

### Debug the Specific Case

Target the specific parameter combination:
```
"args": "tests/test_calc.py::test_divide[10-0] -x"
```

### At the Breakpoint

```
a              # Shows the parameterized values
p numerator    # Check which parameters were used
p denominator
```

---

## Pattern 2: Debugging Fixture Chains

**Scenario**: A test uses multiple fixtures that depend on each other.

### Map the Fixture Dependency

Read `conftest.py` files to understand the fixture chain:
```
test_function(authenticated_client)
  └── authenticated_client(client, user)
        ├── client(app)
        │   └── app(db)
        └── user(db)
            └── db()
```

### Set Breakpoints in Each Fixture

```
b conftest.py:10    # db fixture
b conftest.py:25    # app fixture
b conftest.py:40    # user fixture
b conftest.py:55    # client fixture
b conftest.py:70    # authenticated_client fixture
c
```

### Inspect Data at Each Level

At each breakpoint, verify the fixture produces correct data:
```
p db.tables           # Verify database state
p app.config          # Check app configuration
p user.email          # Verify user creation
p client.cookies      # Check authentication state
```

---

## Pattern 3: Debugging Mock/Patch Issues

**Scenario**: A test uses `unittest.mock` and the mocked behavior is wrong.

### Common Mock Problems

1. **Wrong patch target**: Patching the definition location instead of the import location
2. **Mock not applied**: Forgot `@patch` or context manager
3. **Wrong return value**: Mock returns default `MagicMock()` instead of expected value
4. **Call assertions wrong**: Function called with different args than expected

### Debugging Approach

Start with `--pdb` mode and at the breakpoint:

```
# Check if mock is applied
p type(module.function)          # Should be MagicMock, not function
p module.function.called         # Was it called at all?
p module.function.call_count     # How many times?
p module.function.call_args      # With what arguments?
p module.function.call_args_list # All calls
p module.function.return_value   # What does it return?
```

### Verifying Patch Target

```
# At the breakpoint, check the actual import path
!import sys
!print([k for k in sys.modules if 'module_name' in k])
```

---

## Pattern 4: Debugging Async Test Failures

**Scenario**: An async test fails or hangs.

### Start the Debug Session

```json
{
  "args": "tests/test_async.py::test_async_function -x",
  "python_path": ".venv/bin/python",
  "working_directory": "/project",
  "timeout": 15
}
```

Note: Use higher timeout for async tests as event loop setup may take time.

### Common Async Issues

At the breakpoint:
```
p type(result)          # Is it a coroutine that wasn't awaited?
p result                # Check if it's <coroutine object ...>
```

Common causes:
- Missing `await` keyword
- Missing `@pytest.mark.asyncio` decorator
- Wrong event loop scope
- Async fixtures not properly awaited

---

## Pattern 5: Debugging Database Test Failures

**Scenario**: Tests fail due to database state issues.

### Start with Environment Variables

```json
{
  "args": "tests/test_db.py::test_query -x",
  "python_path": ".venv/bin/python",
  "working_directory": "/project",
  "env": {
    "DATABASE_URL": "sqlite:///test.db",
    "SQLALCHEMY_ECHO": "1"
  }
}
```

### Inspect Database State at Failure

```
p db.session.query(Model).all()       # See all records
p db.session.query(Model).count()     # Count records
p db.session.dirty                     # Uncommitted changes
p db.session.new                       # Newly added objects
p db.session.deleted                   # Objects marked for deletion
```

### Check Transaction State

```
p db.session.is_active
p db.session.in_transaction()
```

---

## Pattern 6: Debugging Test That Passes Alone But Fails in Suite

**Scenario**: Test passes when run individually but fails when run with other tests.

### Reproduce the Failure

Run the full test suite with stop-on-first-failure:
```
"args": "tests/ -x"
```

### Identify State Leakage

At the failure breakpoint:
```
# Check for global state pollution
!import gc; print(len(gc.get_objects()))
p os.environ.get('MODIFIED_VAR')

# Check module-level state
p module.global_variable
p module._cache
```

### Isolate the Interfering Test

Run with `--lf` to re-run the last failed test:
```
"args": "tests/ --lf -x"
```

If it passes alone, the previous test is polluting state. Run the failing test after specific suspect tests:
```
"args": "tests/test_suspect.py tests/test_failing.py -x"
```

---

## Pattern 7: Debugging Test Configuration Issues

**Scenario**: Tests fail due to configuration or environment problems.

### Check pytest Configuration

At the pdb prompt, inspect the effective configuration:
```
!import pytest
!print(pytest.ini_options if hasattr(pytest, 'ini_options') else 'N/A')
```

### Check conftest.py Loading

```
!import sys
p [m for m in sys.modules if 'conftest' in m]
```

### Verify Test Discovery

If tests aren't being found:
```
"args": "tests/ --collect-only"
```

Run with collection only to see what pytest discovers, then debug the actual test.

---

## Pattern 8: Debugging Class-Based Tests

**Scenario**: Test method in a class fails, potentially involving setup/teardown.

### Break at Setup

```
b tests/test_module.py:TestClassName.setUp    # Or setup_method
c
p self                     # Inspect test instance
p self.__dict__            # Instance attributes
```

### Break at Test Method

```
b tests/test_module.py:TestClassName.test_method
c
a                          # See self and other arguments
p self.attribute           # Check instance state from setUp
```

### Check Class Variables vs Instance Variables

```
p type(self).class_var     # Class-level variable
p self.instance_var        # Instance-level variable
p self.__class__.__dict__  # All class attributes
```

---

## Tips for Efficient Pytest Debugging

### Narrow Down Fast

1. Run with `-x` to stop at first failure
2. Use `-k "test_name"` to run only the failing test
3. Use `--lf` to re-run only previously failed tests
4. Use `--no-header -q` for cleaner output

### Read Before Debug

The pytest output often contains:
- The exact assertion that failed
- The actual vs expected values (with diff for complex objects)
- The full traceback
- Local variable values (with `-vv`)

This information may be sufficient to identify the bug without a debug session.

### Use Verbose Mode for Context

```
"args": "tests/test_module.py -x -vv"
```

The `-vv` flag makes pytest show:
- Full assertion introspection
- Complete diffs for collections
- Detailed parametrize info
