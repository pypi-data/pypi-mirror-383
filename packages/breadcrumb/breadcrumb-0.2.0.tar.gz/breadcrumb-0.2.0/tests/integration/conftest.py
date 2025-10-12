"""
Pytest configuration and fixtures for integration tests.

This file is automatically discovered by pytest and makes fixtures
available to all test files in the integration/ directory.
"""

import os
import sys
import tempfile
import uuid
import time
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import pytest

from breadcrumb.storage.connection import reset_manager
from breadcrumb.storage.async_writer import TraceWriter, reset_writer
from breadcrumb import reset_config


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for isolated testing."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, ".breadcrumb", "traces.duckdb")
        yield db_path


@pytest.fixture(autouse=True)
def cleanup_global_state():
    """Reset all global state before and after each test."""
    # Reset before test
    reset_config()
    reset_manager()
    reset_writer()

    yield

    # Reset after test
    try:
        from breadcrumb.storage.connection import _global_manager
        if _global_manager is not None:
            _global_manager.close()
    except:
        pass

    reset_config()
    reset_manager()
    reset_writer()


@pytest.fixture
def sample_traced_code():
    """Return sample Python code that writes trace data to database."""
    return """
import uuid
import time
from datetime import datetime, timezone
from breadcrumb.storage.async_writer import TraceWriter

# Create trace writer
writer = TraceWriter(batch_size=1)
writer.start()

# Write sample trace data
trace_id = str(uuid.uuid4())
writer.write_trace(
    trace_id=trace_id,
    started_at=datetime.now(timezone.utc),
    ended_at=datetime.now(timezone.utc),
    status='completed',
    thread_id=12345
)

# Write trace events
event_id = str(uuid.uuid4())
writer.write_trace_event(
    event_id=event_id,
    trace_id=trace_id,
    timestamp=datetime.now(timezone.utc),
    event_type='call',
    function_name='fibonacci',
    module_name='__main__',
    data={'args': {'n': 5}}
)

event_id2 = str(uuid.uuid4())
writer.write_trace_event(
    event_id=event_id2,
    trace_id=trace_id,
    timestamp=datetime.now(timezone.utc),
    event_type='return',
    function_name='fibonacci',
    module_name='__main__',
    data={'return_value': 5}
)

# Wait for writes and cleanup
time.sleep(0.5)
writer.stop()

print(f"Result: (5, [2, 4, 6, 8, 10])")
"""


@pytest.fixture
def sample_traced_code_with_exception():
    """Return sample Python code with exception handling."""
    return """
from breadcrumb.storage.async_writer import TraceWriter
from breadcrumb.instrumentation.pep669_backend import PEP669Backend
from breadcrumb.instrumentation.settrace_backend import SettraceBackend

# Initialize storage
writer = TraceWriter(batch_size=1)
writer.start()

# Initialize backend
try:
    backend = PEP669Backend(writer)
except (AttributeError, ImportError):
    backend = SettraceBackend(callback=None)

# Start trace
trace_id = backend.start_trace()

def divide(a, b):
    '''Divide two numbers.'''
    return a / b

def main():
    try:
        result = divide(10, 0)
        print(f"Result: {result}")
    except ZeroDivisionError as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    try:
        main()
    finally:
        backend.stop_trace()
        import time
        time.sleep(0.5)
        writer.stop()
"""


@pytest.fixture
def sample_traced_code_with_secrets():
    """Return sample Python code with secrets that should be redacted."""
    return """
from breadcrumb.storage.async_writer import TraceWriter
from breadcrumb.instrumentation.pep669_backend import PEP669Backend
from breadcrumb.instrumentation.settrace_backend import SettraceBackend

# Initialize storage
writer = TraceWriter(batch_size=1)
writer.start()

# Initialize backend
try:
    backend = PEP669Backend(writer)
except (AttributeError, ImportError):
    backend = SettraceBackend(callback=None)

# Start trace
trace_id = backend.start_trace()

def authenticate(username, password, api_key):
    '''Authenticate with credentials.'''
    credentials = {
        'username': username,
        'password': password,
        'api_key': api_key
    }
    return credentials

def main():
    result = authenticate(
        username='alice',
        password='secret123',
        api_key='sk-1234567890abcdef'
    )
    print(f"Authenticated: {result['username']}")

if __name__ == '__main__':
    main()
    backend.stop_trace()
    import time
    time.sleep(0.5)
    writer.stop()
"""


@pytest.fixture
def sample_async_code():
    """Return sample async Python code."""
    return """
import asyncio
from breadcrumb.storage.async_writer import TraceWriter
from breadcrumb.instrumentation.pep669_backend import PEP669Backend
from breadcrumb.instrumentation.settrace_backend import SettraceBackend

# Initialize storage
writer = TraceWriter(batch_size=1)
writer.start()

# Initialize backend
try:
    backend = PEP669Backend(writer)
except (AttributeError, ImportError):
    backend = SettraceBackend(callback=None)

# Start trace
trace_id = backend.start_trace()

async def fetch_data(url):
    '''Simulate async data fetch.'''
    await asyncio.sleep(0.01)
    return f"Data from {url}"

async def process_urls(urls):
    '''Process multiple URLs concurrently.'''
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)

async def main():
    urls = ['http://example.com/1', 'http://example.com/2', 'http://example.com/3']
    results = await process_urls(urls)
    print(f"Fetched {len(results)} items")
    return results

if __name__ == '__main__':
    asyncio.run(main())
    backend.stop_trace()
    import time
    time.sleep(0.5)
    writer.stop()
"""


@pytest.fixture
def sample_multithreaded_code():
    """Return sample multi-threaded Python code."""
    return """
import threading
from breadcrumb.storage.async_writer import TraceWriter
from breadcrumb.instrumentation.pep669_backend import PEP669Backend
from breadcrumb.instrumentation.settrace_backend import SettraceBackend

# Initialize storage
writer = TraceWriter(batch_size=1)
writer.start()

# Initialize backend
try:
    backend = PEP669Backend(writer)
except (AttributeError, ImportError):
    backend = SettraceBackend(callback=None)

# Start trace
trace_id = backend.start_trace()

results = []
results_lock = threading.Lock()

def worker(worker_id, iterations):
    '''Worker thread that performs calculations.'''
    local_results = []
    for i in range(iterations):
        value = worker_id * 100 + i
        local_results.append(value * 2)

    with results_lock:
        results.extend(local_results)

def main():
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i, 5))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"Total results: {len(results)}")

if __name__ == '__main__':
    main()
    backend.stop_trace()
    import time
    time.sleep(0.5)
    writer.stop()
"""


def run_traced_code(code: str, db_path: str, env: Optional[dict] = None) -> dict:
    """
    Run Python code with tracing enabled and return execution results.

    Args:
        code: Python code to execute
        db_path: Database path for traces
        env: Optional environment variables

    Returns:
        Dict with returncode, stdout, stderr, db_path
    """
    import subprocess

    # Create a temporary file for the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Inject db_path configuration at the top
        db_config = f"""
import os
os.environ['BREADCRUMB_DB_PATH'] = r'{db_path}'
"""
        f.write(db_config + code)
        temp_file = f.name

    try:
        # Set up environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)

        # Run the code
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10,
            env=exec_env
        )

        # Give async writer time to flush
        time.sleep(0.3)

        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'db_path': db_path
        }
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass


def wait_for_traces(db_path: str, min_traces: int = 1, timeout: float = 5.0) -> bool:
    """
    Wait for traces to be written to the database.

    Args:
        db_path: Database path
        min_traces: Minimum number of traces expected
        timeout: Maximum time to wait

    Returns:
        True if traces found, False if timeout
    """
    from breadcrumb.storage.query import query_traces

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            traces = query_traces("SELECT * FROM traces", db_path=db_path)
            if len(traces) >= min_traces:
                return True
        except:
            pass

        time.sleep(0.1)

    return False


# Make helper functions available as module-level imports
__all__ = ['run_traced_code', 'wait_for_traces']
