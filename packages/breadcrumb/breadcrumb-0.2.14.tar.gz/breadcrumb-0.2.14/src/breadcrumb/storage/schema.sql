-- Breadcrumb AI Tracer - DuckDB Schema
-- Version: 1.0
-- Description: Optimized schema for trace storage with query performance in mind

-- Schema version tracking table
CREATE TABLE IF NOT EXISTS _breadcrumb_schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Main traces table
-- Stores high-level trace metadata
CREATE TABLE IF NOT EXISTS traces (
    id VARCHAR PRIMARY KEY,                 -- UUID as string
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    status VARCHAR,                         -- 'running', 'completed', 'failed'
    thread_id BIGINT,
    metadata JSON,                          -- Additional trace-level metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trace events table
-- Stores individual execution events (calls, returns, lines, exceptions)
CREATE TABLE IF NOT EXISTS trace_events (
    id VARCHAR PRIMARY KEY,                 -- UUID as string
    trace_id VARCHAR NOT NULL,              -- FK to traces.id
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR NOT NULL,            -- 'call', 'return', 'line', 'exception'
    function_name VARCHAR,
    module_name VARCHAR,
    file_path VARCHAR,
    line_number INTEGER,
    data JSON,                              -- Event-specific data (args, return values, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Variables table
-- Stores captured variable values from trace events
CREATE TABLE IF NOT EXISTS variables (
    id VARCHAR PRIMARY KEY,                 -- UUID as string
    event_id VARCHAR NOT NULL,              -- FK to trace_events.id
    name VARCHAR NOT NULL,
    value JSON,                             -- Variable value (serialized)
    type VARCHAR,                           -- Python type name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exceptions table
-- Stores exception details from trace events
CREATE TABLE IF NOT EXISTS exceptions (
    id VARCHAR PRIMARY KEY,                 -- UUID as string
    event_id VARCHAR NOT NULL,              -- FK to trace_events.id
    trace_id VARCHAR NOT NULL,              -- FK to traces.id (denormalized for query performance)
    exception_type VARCHAR NOT NULL,
    message TEXT,
    stack_trace TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for query performance
-- Trace events indexes
CREATE INDEX IF NOT EXISTS idx_trace_events_trace_id ON trace_events(trace_id);
CREATE INDEX IF NOT EXISTS idx_trace_events_timestamp ON trace_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_trace_events_function_name ON trace_events(function_name);
CREATE INDEX IF NOT EXISTS idx_trace_events_event_type ON trace_events(event_type);
CREATE INDEX IF NOT EXISTS idx_trace_events_module ON trace_events(module_name);

-- Traces indexes
CREATE INDEX IF NOT EXISTS idx_traces_started_at ON traces(started_at);
CREATE INDEX IF NOT EXISTS idx_traces_status ON traces(status);
CREATE INDEX IF NOT EXISTS idx_traces_thread_id ON traces(thread_id);

-- Exceptions indexes
CREATE INDEX IF NOT EXISTS idx_exceptions_trace_id ON exceptions(trace_id);
CREATE INDEX IF NOT EXISTS idx_exceptions_type ON exceptions(exception_type);
CREATE INDEX IF NOT EXISTS idx_exceptions_event_id ON exceptions(event_id);

-- Variables indexes
CREATE INDEX IF NOT EXISTS idx_variables_event_id ON variables(event_id);
CREATE INDEX IF NOT EXISTS idx_variables_name ON variables(name);

-- Insert initial schema version
INSERT INTO _breadcrumb_schema_version (version, description)
VALUES (1, 'Initial schema with traces, events, variables, and exceptions tables')
ON CONFLICT DO NOTHING;
