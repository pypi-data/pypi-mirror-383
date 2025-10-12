# lu — a vcr-style record/replay stubbing library for Python methods

lu (录) — Chinese for "recording".

lu provides a small context manager, `record()`, which can patch module-qualified functions or instance methods to record return values (or exceptions) to compressed pickle files and generate a `manifest.json` describing the recordings.

On the first run, the patched methods execute normally and their outputs are recorded. Subsequent runs replay the recorded return values (or re-raise recorded exceptions) instead of executing the original code — similar to how HTTP cassette libraries like vcrpy work, but for arbitrary Python methods.

## Quickstart

Install from PyPI:

```bash
pip install lu-python
```

Basic usage:

```python
import lu

with lu.record(
    target={
        'module1.Foo.expensive_method1': ['arg1', 'kwarg1'],
        'package2.module2.expensive_method2': ['arg2'],
    },
    recordings_dir='tests/fixtures/recordings/',
):
    from module1 import Foo
    foo = Foo()
    foo.expensive_method('bar', kwarg1=3)

    from package2 import module2
    module2.expensive_method2('baz')
```

See `tests/test_lu.py` for more examples.

## Using with pytest

Add an autouse fixture (for example in `tests/conftest.py`) to enable recording/replay for the test session:

```python
import pytest
import lu

@pytest.fixture(scope='session', autouse=True)
def stub_calls():
    with lu.record(
        target={
            # 'module.Class.method': ['arg_name', 'kwarg_name'],
            # add targets you want recorded here
        },
        recordings_dir='tests/fixtures/recordings/',
    ):
        yield
```

## How lu differs from other tools

I wrote `lu` because I couldn't find a simple record/replay tool for arbitrary Python methods. A few alternatives exist but they don't match this use case:

- `testcontainers`: runs real services in Docker, which requires setup and infrastructure and does not provide automatic request/response recording.
- `keploy`: captures and replays network calls at a lower level; powerful but heavier-weight.
- `vcrpy` / `pytest-recordings`: focused on HTTP clients (requests/urllib3) only.
- `unittest.mock`: flexible but manual — `lu` provides an automated record-and-replay workflow on top of method patching.

`lu` works at the method level, so you can record calls to client libraries (e.g., database drivers, HTTP clients) or your own functions.

## Limitations

- Prefer using `lu` for read-only calls. While you can record methods with side effects (for example, database writes), `lu` does not maintain external state. Replaying a recorded write will not update a database or other external system.
- No transaction or rollback support. `lu` records and replays return values and exceptions only.

## Contributing

Contributions and bug reports are welcome. Please open an issue or submit a pull request with tests that demonstrate the change or fix.

## License

This project is provided under the terms of the repository license. See the `LICENSE` file for details.
