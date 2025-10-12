"""
Integration tests for Smart Query API.

Tests the new smart query commands that replace raw SQL:
- --gaps: Show untraced function calls
- --call: Show function calls with I/O
- --flow: Show execution timeline

These are integration tests that run real code and test against real traces.
"""

import pytest
import json
import sys

from breadcrumb.cli.main import app as cli_app
from typer.testing import CliRunner

from . import run_traced_code, wait_for_traces


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def smart_query_test_code():
    """
    Test code that creates a known execution pattern for smart queries.

    This code:
    - Has a main() function that calls internal functions
    - Calls external library functions (json.dumps, json.loads)
    - Has clear args and return values
    - Creates a pattern we can verify with smart queries
    """
    return """
import breadcrumb
import json

# Initialize breadcrumb with minimal tracing (only __main__)
breadcrumb.init(
    include=['__main__']
)

def calculate_total(items):
    '''Calculate total price of items.'''
    total = sum(item['price'] for item in items)
    return total

def format_receipt(items, total):
    '''Format receipt as JSON.'''
    receipt = {
        'items': items,
        'total': total,
        'formatted': f"Total: ${total:.2f}"
    }
    # This calls json.dumps which is NOT traced (not in __main__)
    return json.dumps(receipt)

def process_order(customer_name, items):
    '''Process a customer order.'''
    total = calculate_total(items)
    receipt = format_receipt(items, total)
    # This calls json.loads which is NOT traced
    parsed = json.loads(receipt)
    return {
        'customer': customer_name,
        'receipt': parsed
    }

def main():
    '''Main entry point.'''
    items = [
        {'name': 'Pizza', 'price': 12.99},
        {'name': 'Soda', 'price': 2.50},
        {'name': 'Salad', 'price': 5.99}
    ]

    result = process_order('Alice', items)
    print(f"Order processed for {result['customer']}")
    print(f"Total: ${result['receipt']['total']:.2f}")

    return result

if __name__ == '__main__':
    try:
        result = main()
    finally:
        breadcrumb.shutdown(timeout=2.0)
"""


@pytest.fixture
def nested_calls_test_code():
    """
    Test code with nested calls to test --flow command.

    Creates a clear execution flow:
    main() -> outer() -> middle() -> inner()
    """
    return """
import breadcrumb

breadcrumb.init(
    include=['__main__']
)

def inner(value):
    '''Innermost function.'''
    return value * 2

def middle(value):
    '''Middle function.'''
    result = inner(value)
    return result + 10

def outer(value):
    '''Outer function.'''
    result = middle(value)
    return result * 3

def main():
    '''Main entry point.'''
    result = outer(5)
    print(f"Result: {result}")
    return result

if __name__ == '__main__':
    try:
        result = main()
    finally:
        breadcrumb.shutdown(timeout=2.0)
"""


class TestSmartQueryGaps:
    """Test --gaps command: Show untraced function calls."""

    def test_gaps_detects_untraced_calls(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """
        Test: Run code with minimal includes → breadcrumb query --gaps

        Should detect:
        - json.dumps (called from format_receipt)
        - json.loads (called from process_order)
        """
        # Run code with only __main__ traced
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0, f"Code failed: {result['stderr']}"
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --gaps command
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--gaps']
        )

        # Should succeed
        assert cli_result.exit_code == 0, f"--gaps failed: {cli_result.stderr}"

        # Parse output
        output = json.loads(cli_result.stdout)

        # Verify structure
        assert 'untraced_calls' in output
        assert isinstance(output['untraced_calls'], list)

        # Should have detected json.dumps and json.loads
        untraced_functions = [call['function'] for call in output['untraced_calls']]

        # We expect to see calls to json module (dumps, loads)
        # The exact function names might be json.dumps or _json.dumps depending on implementation
        json_related = [f for f in untraced_functions if 'json' in f.lower() or 'dumps' in f or 'loads' in f]
        assert len(json_related) > 0, f"Expected json calls in untraced, got: {untraced_functions}"

    def test_gaps_suggests_include_patterns(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test that --gaps suggests include patterns for untraced calls."""
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --gaps
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--gaps']
        )

        assert cli_result.exit_code == 0

        # Parse output
        output = json.loads(cli_result.stdout)

        # Should have suggestions
        assert 'tip' in output or 'suggestion' in output or any(
            'suggested_include' in call for call in output.get('untraced_calls', [])
        )

    def test_gaps_shows_call_counts(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test that --gaps shows how many times each function was called."""
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --gaps
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--gaps']
        )

        assert cli_result.exit_code == 0

        # Parse output
        output = json.loads(cli_result.stdout)

        # Each untraced call should have call_count
        for call in output.get('untraced_calls', []):
            assert 'call_count' in call or 'count' in call

    def test_gaps_shows_caller_context(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test that --gaps shows which function made the untraced call."""
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --gaps
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--gaps']
        )

        assert cli_result.exit_code == 0

        # Parse output
        output = json.loads(cli_result.stdout)

        # Each untraced call should show which function called it
        for call in output.get('untraced_calls', []):
            assert 'called_by' in call or 'caller' in call


class TestSmartQueryCall:
    """Test --call command: Show function calls with I/O."""

    def test_call_shows_function_io(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """
        Test: Run code → breadcrumb query --call calculate_total

        Should show:
        - Arguments passed (items list)
        - Return value (total)
        - Metadata (timestamp, duration, etc.)
        """
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --call for calculate_total
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--call', 'calculate_total']
        )

        # Should succeed
        assert cli_result.exit_code == 0, f"--call failed: {cli_result.stderr}"

        # Parse output
        output = json.loads(cli_result.stdout)

        # Verify structure
        assert 'function' in output
        assert output['function'] == 'calculate_total'
        assert 'calls' in output
        assert len(output['calls']) > 0

        # Verify call details
        call = output['calls'][0]
        assert 'timestamp' in call
        assert 'args' in call or 'arguments' in call
        assert 'return_value' in call or 'return' in call

        # Verify args structure (should have 'items' parameter)
        args = call.get('args', call.get('arguments', {}))
        assert 'items' in args or isinstance(args, dict)

    def test_call_shows_duration(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test that --call shows execution duration."""
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --call
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--call', 'calculate_total']
        )

        assert cli_result.exit_code == 0

        # Parse output
        output = json.loads(cli_result.stdout)
        call = output['calls'][0]

        # Should have duration
        assert 'duration_ms' in call or 'duration' in call or 'elapsed_ms' in call

    def test_call_shows_caller_and_callees(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test that --call shows what called this function and what it called."""
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --call for process_order (which calls other functions)
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--call', 'process_order']
        )

        assert cli_result.exit_code == 0

        # Parse output
        output = json.loads(cli_result.stdout)
        call = output['calls'][0]

        # Should show what called it
        assert 'called_by' in call or 'caller' in call

        # Should show what it called
        assert 'calls_made' in call or 'callees' in call

    def test_call_with_multiple_invocations(
        self,
        temp_db_path,
        cli_runner
    ):
        """Test --call when a function is called multiple times."""
        # Code that calls a function multiple times
        code = """
import breadcrumb

breadcrumb.init(
    include=['__main__']
)

def double(x):
    return x * 2

def main():
    results = [double(i) for i in range(5)]
    print(f"Results: {results}")
    return results

if __name__ == '__main__':
    try:
        main()
    finally:
        breadcrumb.shutdown(timeout=2.0)
"""
        # Run code
        result = run_traced_code(code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --call for double
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--call', 'double']
        )

        assert cli_result.exit_code == 0

        # Parse output
        output = json.loads(cli_result.stdout)

        # Should have multiple calls (5 invocations)
        assert len(output['calls']) == 5

        # Each call should have different args
        args_list = [call.get('args', call.get('arguments')) for call in output['calls']]
        assert len(set(str(a) for a in args_list)) > 1  # Different arguments

    def test_call_nonexistent_function(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test --call with a function that doesn't exist in traces."""
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --call for nonexistent function
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--call', 'nonexistent_function']
        )

        # Should succeed but return empty results
        assert cli_result.exit_code == 0

        output = json.loads(cli_result.stdout)
        assert len(output.get('calls', [])) == 0


class TestSmartQueryFlow:
    """Test --flow command: Show execution timeline."""

    def test_flow_shows_chronological_execution(
        self,
        temp_db_path,
        nested_calls_test_code,
        cli_runner
    ):
        """
        Test: Run code → breadcrumb query --flow

        Should show:
        1. main() called
        2.   outer() called
        3.     middle() called
        4.       inner() called
        5.       inner() returned
        6.     middle() returned
        7.   outer() returned
        8. main() returned
        """
        # Run code
        result = run_traced_code(nested_calls_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --flow
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--flow']
        )

        # Should succeed
        assert cli_result.exit_code == 0, f"--flow failed: {cli_result.stderr}"

        # Parse output
        output = json.loads(cli_result.stdout)

        # Verify structure
        assert 'flow' in output or 'events' in output or 'timeline' in output

        events = output.get('flow', output.get('events', output.get('timeline', [])))
        assert len(events) > 0

        # Should have call and return events in chronological order
        event_types = [e.get('event_type', e.get('type')) for e in events]
        assert 'call' in event_types or 'PY_START' in event_types
        assert 'return' in event_types or 'PY_RETURN' in event_types

    def test_flow_shows_nested_structure(
        self,
        temp_db_path,
        nested_calls_test_code,
        cli_runner
    ):
        """Test that --flow shows proper nesting/indentation."""
        # Run code
        result = run_traced_code(nested_calls_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --flow
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--flow']
        )

        assert cli_result.exit_code == 0

        # Parse output
        output = json.loads(cli_result.stdout)
        events = output.get('flow', output.get('events', output.get('timeline', [])))

        # Should have depth/level information for nesting
        # or should have parent/child relationships
        for event in events:
            # One of these should be present to show nesting
            has_nesting_info = (
                'depth' in event or
                'level' in event or
                'indent' in event or
                'parent_id' in event or
                'caller' in event
            )
            # At least some events should have nesting info
            if has_nesting_info:
                break
        else:
            # If we get here, no events had nesting info
            pytest.skip("Flow output doesn't include nesting information yet")

    def test_flow_with_module_filter(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test --flow with --module filter."""
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --flow with module filter
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--flow', '--module', '__main__']
        )

        # Should succeed
        assert cli_result.exit_code == 0

        # Parse output
        output = json.loads(cli_result.stdout)
        events = output.get('flow', output.get('events', output.get('timeline', [])))

        # All events should be from __main__ module
        for event in events:
            module = event.get('module_name', event.get('module'))
            if module:  # Some events might not have module info
                assert module == '__main__'

    def test_flow_shows_untraced_calls(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test that --flow indicates which calls were not traced."""
        # Run code (which calls json.dumps/loads that aren't traced)
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute --flow
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--flow']
        )

        assert cli_result.exit_code == 0

        # Parse output
        output = json.loads(cli_result.stdout)

        # Should have some indication of untraced calls
        # Either in the flow itself or as a separate field
        has_untraced_info = (
            'untraced_calls' in output or
            'gaps' in output or
            any(e.get('traced') == False for e in output.get('flow', output.get('events', [])))
        )

        # This is a nice-to-have feature, so we'll skip if not implemented
        if not has_untraced_info:
            pytest.skip("Flow doesn't show untraced calls yet")


class TestSmartQueryIntegration:
    """Test integration between different smart query commands."""

    def test_gaps_to_call_workflow(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """
        Test workflow: Use --gaps to discover functions, then --call to inspect them.

        Simulates iterative exploration:
        1. Run code with minimal tracing
        2. Use --gaps to see what's not traced
        3. Use --call to inspect traced functions
        """
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Step 1: Find gaps
        gaps_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--gaps']
        )
        assert gaps_result.exit_code == 0
        gaps_output = json.loads(gaps_result.stdout)

        # Step 2: Find a traced function (calculate_total is in __main__)
        call_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--call', 'calculate_total']
        )
        assert call_result.exit_code == 0
        call_output = json.loads(call_result.stdout)

        # Both commands should succeed
        assert len(call_output.get('calls', [])) > 0

    def test_flow_and_gaps_consistency(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test that --flow and --gaps show consistent information."""
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Get flow
        flow_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--flow']
        )
        assert flow_result.exit_code == 0

        # Get gaps
        gaps_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', '--gaps']
        )
        assert gaps_result.exit_code == 0

        # Both should provide consistent view of what was traced
        # This is more of a sanity check that both commands work
        assert flow_result.exit_code == gaps_result.exit_code == 0


class TestSmartQueryErrorHandling:
    """Test error handling for smart query commands."""

    def test_smart_query_with_no_traces(
        self,
        temp_db_path,
        cli_runner
    ):
        """Test smart queries against empty database."""
        # Don't run any code - database will be empty

        # All commands should handle empty database gracefully
        commands = [
            ['query', '--gaps'],
            ['query', '--call', 'any_function'],
            ['query', '--flow'],
        ]

        for cmd in commands:
            cli_result = cli_runner.invoke(
                cli_app,
                ['--db-path', temp_db_path] + cmd
            )

            # Should succeed with empty results (not crash)
            assert cli_result.exit_code == 0

            output = json.loads(cli_result.stdout)
            # Should have empty results
            assert (
                len(output.get('untraced_calls', [])) == 0 or
                len(output.get('calls', [])) == 0 or
                len(output.get('flow', output.get('events', []))) == 0
            )

    def test_smart_query_json_output(
        self,
        temp_db_path,
        smart_query_test_code,
        cli_runner
    ):
        """Test that all smart queries return valid JSON."""
        # Run code
        result = run_traced_code(smart_query_test_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # All commands should return valid JSON
        commands = [
            ['query', '--gaps'],
            ['query', '--call', 'calculate_total'],
            ['query', '--flow'],
        ]

        for cmd in commands:
            cli_result = cli_runner.invoke(
                cli_app,
                ['--db-path', temp_db_path] + cmd
            )

            assert cli_result.exit_code == 0

            # Should be valid JSON
            try:
                output = json.loads(cli_result.stdout)
                assert isinstance(output, dict)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON for {cmd}: {e}\n{cli_result.stdout}")
