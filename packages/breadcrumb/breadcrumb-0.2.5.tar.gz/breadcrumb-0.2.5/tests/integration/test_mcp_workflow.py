"""
MCP workflow integration tests for Breadcrumb AI Tracer.

Tests the Model Context Protocol (MCP) server integration:
1. Run traced application
2. Start MCP server
3. Call MCP tools
4. Verify AI agent workflow
"""

import pytest
import json
import time

from breadcrumb.mcp.server import create_mcp_server
from breadcrumb.storage.query import query_traces, QueryError

from . import (
    run_traced_code,
    wait_for_traces,
)


class TestMCPServerCreation:
    """Test MCP server creation and initialization."""

    def test_create_mcp_server_with_db_path(self, temp_db_path, sample_traced_code):
        """Test creating MCP server with explicit database path."""
        # Create database first
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)

        # Verify server is created
        assert mcp is not None
        assert hasattr(mcp, 'db_path')
        assert mcp.db_path == temp_db_path

    def test_create_mcp_server_missing_database(self, temp_db_path):
        """Test that creating MCP server with missing database raises error."""
        with pytest.raises(FileNotFoundError, match="Database not found"):
            create_mcp_server(db_path=temp_db_path)


class TestMCPQueryTracesTool:
    """Test breadcrumb__query_traces MCP tool."""

    def test_query_traces_tool_basic(self, temp_db_path, sample_traced_code):
        """Test: Run app → MCP query_traces → verify JSON response."""
        # Setup: Run traced code
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)

        # Get the tool function
        # FastMCP stores tools internally, we need to access them
        tools = mcp._tools
        assert 'breadcrumb__query_traces' in tools, "query_traces tool not registered"

        query_tool = tools['breadcrumb__query_traces']

        # Call the tool
        response_str = query_tool.fn(sql="SELECT * FROM traces LIMIT 10")

        # Parse JSON response
        response = json.loads(response_str)

        # Verify response structure
        assert 'traces' in response
        assert 'total' in response
        assert 'query_time_ms' in response
        assert 'schema_version' in response

        # Verify data
        assert response['total'] > 0, "No traces returned"
        assert len(response['traces']) > 0
        assert isinstance(response['query_time_ms'], int)

    def test_query_traces_tool_with_filter(self, temp_db_path, sample_traced_code):
        """Test query_traces with WHERE clause."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)
        query_tool = mcp._tools['breadcrumb__query_traces']

        # Query with filter
        response_str = query_tool.fn(
            sql="SELECT * FROM traces WHERE status = 'completed' LIMIT 5"
        )
        response = json.loads(response_str)

        # Verify filtering worked
        assert response['total'] >= 0
        for trace in response['traces']:
            assert trace['status'] == 'completed'

    def test_query_traces_tool_unsafe_query_rejected(self, temp_db_path, sample_traced_code):
        """Test that unsafe SQL queries are rejected by MCP tool."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)
        query_tool = mcp._tools['breadcrumb__query_traces']

        # Try unsafe queries
        unsafe_queries = [
            "DELETE FROM traces",
            "DROP TABLE traces",
            "UPDATE traces SET status='hacked'",
            "INSERT INTO traces VALUES (...)",
        ]

        for unsafe_sql in unsafe_queries:
            response_str = query_tool.fn(sql=unsafe_sql)
            response = json.loads(response_str)

            # Should return error response
            assert 'error' in response
            assert 'InvalidQueryError' in response['error']

    def test_query_traces_tool_empty_database(self, temp_db_path):
        """Test query_traces tool with empty database."""
        # Create empty database by running minimal code
        minimal_code = """
import breadcrumb
breadcrumb.init(silent=True)
print("Done")
"""
        result = run_traced_code(minimal_code, temp_db_path)
        assert result['returncode'] == 0
        time.sleep(0.3)

        # Create MCP server
        try:
            mcp = create_mcp_server(db_path=temp_db_path)
            query_tool = mcp._tools['breadcrumb__query_traces']

            # Query empty database
            response_str = query_tool.fn(sql="SELECT * FROM traces")
            response = json.loads(response_str)

            # Should handle gracefully (either empty results or error)
            assert 'traces' in response or 'error' in response

        except FileNotFoundError:
            # Database might not be created if no traces were generated
            pytest.skip("Database not created (no traces generated)")


class TestMCPGetTraceTool:
    """Test breadcrumb__get_trace MCP tool."""

    def test_get_trace_tool_basic(self, temp_db_path, sample_traced_code):
        """Test: Run app → MCP get_trace → verify full trace details."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Get a trace ID
        traces = query_traces("SELECT id FROM traces LIMIT 1", db_path=temp_db_path)
        trace_id = traces[0]['id']

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)
        get_trace_tool = mcp._tools['breadcrumb__get_trace']

        # Call the tool
        response_str = get_trace_tool.fn(trace_id=trace_id)
        response = json.loads(response_str)

        # Verify response structure
        assert 'trace' in response
        assert 'events' in response
        assert 'exceptions' in response
        assert 'summary' in response

        # Verify summary
        summary = response['summary']
        assert summary['trace_id'] == trace_id
        assert 'status' in summary
        assert 'event_count' in summary
        assert 'exception_count' in summary

        # Verify trace details
        assert response['trace']['id'] == trace_id

    def test_get_trace_tool_nonexistent_trace(self, temp_db_path, sample_traced_code):
        """Test get_trace with non-existent trace ID."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)
        get_trace_tool = mcp._tools['breadcrumb__get_trace']

        # Try to get non-existent trace
        fake_id = "00000000-0000-0000-0000-000000000000"
        response_str = get_trace_tool.fn(trace_id=fake_id)
        response = json.loads(response_str)

        # Should return error
        assert 'error' in response
        assert response['error'] == 'TraceNotFoundError'
        assert fake_id in response['message']


class TestMCPFindExceptionsTool:
    """Test breadcrumb__find_exceptions MCP tool."""

    def test_find_exceptions_tool_basic(
        self,
        temp_db_path,
        sample_traced_code_with_exception,
    ):
        """Test: Run app with exception → MCP find_exceptions → verify results."""
        # Run code with exception
        result = run_traced_code(sample_traced_code_with_exception, temp_db_path)
        # Should fail with exception
        assert result['returncode'] != 0

        # Wait for traces
        time.sleep(0.5)

        # Create MCP server
        try:
            mcp = create_mcp_server(db_path=temp_db_path)
        except FileNotFoundError:
            pytest.skip("Database not created")

        find_exceptions_tool = mcp._tools['breadcrumb__find_exceptions']

        # Call the tool
        response_str = find_exceptions_tool.fn(since="1h", limit=10)
        response = json.loads(response_str)

        # Verify response structure
        assert 'exceptions' in response
        assert 'total' in response
        assert 'time_range' in response
        assert 'limit' in response

        # Verify time range
        assert response['time_range'] == "1h"
        assert response['limit'] == 10

        # Verify exceptions (if captured)
        if response['total'] > 0:
            exc = response['exceptions'][0]
            assert 'exception_type' in exc
            assert exc['exception_type'] == 'ZeroDivisionError'

    def test_find_exceptions_tool_time_ranges(self, temp_db_path, sample_traced_code):
        """Test find_exceptions with different time ranges."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)
        find_exceptions_tool = mcp._tools['breadcrumb__find_exceptions']

        # Test different time ranges
        time_ranges = ["30m", "2h", "1d"]

        for since in time_ranges:
            response_str = find_exceptions_tool.fn(since=since, limit=5)
            response = json.loads(response_str)

            # Should succeed with valid structure
            assert 'exceptions' in response
            assert 'total' in response
            assert response['time_range'] == since

    def test_find_exceptions_tool_invalid_time_range(self, temp_db_path, sample_traced_code):
        """Test find_exceptions with invalid time range."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)
        find_exceptions_tool = mcp._tools['breadcrumb__find_exceptions']

        # Try invalid time range
        response_str = find_exceptions_tool.fn(since="invalid", limit=5)
        response = json.loads(response_str)

        # Should return error
        assert 'error' in response
        assert response['error'] == 'ValueError'


class TestMCPAnalyzePerformanceTool:
    """Test breadcrumb__analyze_performance MCP tool."""

    def test_analyze_performance_tool_basic(self, temp_db_path, sample_traced_code):
        """Test: Run app → MCP analyze_performance → verify statistics."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Get a function name
        events = query_traces(
            "SELECT DISTINCT function_name FROM trace_events WHERE function_name IS NOT NULL LIMIT 1",
            db_path=temp_db_path
        )

        if len(events) == 0:
            pytest.skip("No function names captured")

        function_name = events[0]['function_name']

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)
        analyze_perf_tool = mcp._tools['breadcrumb__analyze_performance']

        # Call the tool
        response_str = analyze_perf_tool.fn(function=function_name, limit=5)
        response = json.loads(response_str)

        # Verify response structure
        assert 'function' in response
        assert 'statistics' in response
        assert 'slowest_traces' in response

        # Verify function name
        assert response['function'] == function_name

        # Verify statistics
        stats = response['statistics']
        assert 'call_count' in stats
        assert 'avg_duration_ms' in stats
        assert 'min_duration_ms' in stats
        assert 'max_duration_ms' in stats

    def test_analyze_performance_tool_nonexistent_function(
        self,
        temp_db_path,
        sample_traced_code,
    ):
        """Test analyze_performance with non-existent function."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)
        analyze_perf_tool = mcp._tools['breadcrumb__analyze_performance']

        # Try non-existent function
        response_str = analyze_perf_tool.fn(function="nonexistent_function", limit=5)
        response = json.loads(response_str)

        # Should return error or empty results
        assert 'error' in response or 'statistics' in response

        if 'error' in response:
            assert response['error'] == 'FunctionNotFound'


class TestMCPWorkflowScenarios:
    """Test complete MCP workflow scenarios."""

    def test_ai_agent_debugging_workflow(
        self,
        temp_db_path,
        sample_traced_code_with_exception,
    ):
        """
        Test AI agent workflow: Find exception → Get trace details → Analyze context.

        This simulates how Claude would debug an issue.
        """
        # Step 1: Run code with exception
        result = run_traced_code(sample_traced_code_with_exception, temp_db_path)
        assert result['returncode'] != 0
        time.sleep(0.5)

        # Step 2: Create MCP server
        try:
            mcp = create_mcp_server(db_path=temp_db_path)
        except FileNotFoundError:
            pytest.skip("Database not created")

        # Step 3: Find exceptions (what AI would do first)
        find_exceptions_tool = mcp._tools['breadcrumb__find_exceptions']
        exceptions_response = find_exceptions_tool.fn(since="1h", limit=10)
        exceptions_data = json.loads(exceptions_response)

        if exceptions_data['total'] == 0:
            pytest.skip("No exceptions captured")

        # Step 4: Get trace ID from exception
        first_exception = exceptions_data['exceptions'][0]
        trace_id = first_exception['trace_id']

        # Step 5: Get full trace details (what AI would do next)
        get_trace_tool = mcp._tools['breadcrumb__get_trace']
        trace_response = get_trace_tool.fn(trace_id=trace_id)
        trace_data = json.loads(trace_response)

        # Step 6: Verify AI has all context for debugging
        assert 'trace' in trace_data
        assert 'events' in trace_data
        assert 'exceptions' in trace_data

        # AI can now see:
        # - The exception type and message
        # - All events leading up to the exception
        # - Full trace context

    def test_ai_agent_performance_analysis_workflow(self, temp_db_path, sample_traced_code):
        """
        Test AI agent workflow: Query functions → Analyze performance → Find bottlenecks.

        This simulates how Claude would analyze performance.
        """
        # Step 1: Run code
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Step 2: Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)

        # Step 3: Find all functions (what AI would do first)
        query_tool = mcp._tools['breadcrumb__query_traces']
        functions_response = query_tool.fn(
            sql="SELECT DISTINCT function_name FROM trace_events WHERE function_name IS NOT NULL"
        )
        functions_data = json.loads(functions_response)

        if functions_data['total'] == 0:
            pytest.skip("No functions captured")

        # Step 4: Analyze each function's performance
        analyze_perf_tool = mcp._tools['breadcrumb__analyze_performance']

        for func_row in functions_data['traces'][:3]:  # Limit to 3 functions
            function_name = func_row['function_name']

            perf_response = analyze_perf_tool.fn(function=function_name, limit=5)
            perf_data = json.loads(perf_response)

            # Verify AI gets performance statistics
            if 'statistics' in perf_data:
                stats = perf_data['statistics']
                assert 'call_count' in stats
                assert 'avg_duration_ms' in stats

                # AI can now identify slow functions
                # and examine the slowest traces

    def test_mcp_response_size_handling(self, temp_db_path):
        """Test that MCP tools handle large responses correctly."""
        # Create code that generates many traces
        code = """
import breadcrumb

breadcrumb.init(silent=True)

def generate_traces():
    for i in range(50):
        value = i * 2
    return value

def main():
    for _ in range(10):
        generate_traces()
    print("Done")

if __name__ == '__main__':
    main()
"""

        result = run_traced_code(code, temp_db_path)
        assert result['returncode'] == 0
        time.sleep(0.5)

        # Create MCP server
        try:
            mcp = create_mcp_server(db_path=temp_db_path)
        except FileNotFoundError:
            pytest.skip("Database not created")

        # Query all traces (might be large)
        query_tool = mcp._tools['breadcrumb__query_traces']
        response_str = query_tool.fn(sql="SELECT * FROM trace_events")
        response = json.loads(response_str)

        # Verify response is valid JSON
        assert 'traces' in response or 'error' in response

        # Check if response was truncated due to size
        if 'warning' in response:
            assert 'truncated' in response['warning'].lower()


class TestMCPToolsRegistration:
    """Test that all MCP tools are properly registered."""

    def test_all_tools_registered(self, temp_db_path, sample_traced_code):
        """Test that all 4 MCP tools are registered."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)

        # Verify all tools are registered
        expected_tools = [
            'breadcrumb__query_traces',
            'breadcrumb__get_trace',
            'breadcrumb__find_exceptions',
            'breadcrumb__analyze_performance',
        ]

        for tool_name in expected_tools:
            assert tool_name in mcp._tools, f"Tool {tool_name} not registered"

    def test_tool_metadata(self, temp_db_path, sample_traced_code):
        """Test that tools have proper metadata."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Create MCP server
        mcp = create_mcp_server(db_path=temp_db_path)

        # Check each tool has a function
        for tool_name, tool in mcp._tools.items():
            assert hasattr(tool, 'fn'), f"Tool {tool_name} missing function"
            assert callable(tool.fn), f"Tool {tool_name} function not callable"
