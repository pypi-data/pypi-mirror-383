-- Migration v1: Initial schema
-- Description: Creates base tables for traces, events, variables, and exceptions
-- Date: 2025-10-10

-- Schema version tracking table
CREATE TABLE IF NOT EXISTS _breadcrumb_schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Main traces table
CREATE TABLE IF NOT EXISTS traces (
    id VARCHAR PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    status VARCHAR,
    thread_id BIGINT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trace events table
CREATE TABLE IF NOT EXISTS trace_events (
    id VARCHAR PRIMARY KEY,
    trace_id VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR NOT NULL,
    function_name VARCHAR,
    module_name VARCHAR,
    file_path VARCHAR,
    line_number INTEGER,
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Variables table
CREATE TABLE IF NOT EXISTS variables (
    id VARCHAR PRIMARY KEY,
    event_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    value JSON,
    type VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exceptions table
CREATE TABLE IF NOT EXISTS exceptions (
    id VARCHAR PRIMARY KEY,
    event_id VARCHAR NOT NULL,
    trace_id VARCHAR NOT NULL,
    exception_type VARCHAR NOT NULL,
    message TEXT,
    stack_trace TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_trace_events_trace_id ON trace_events(trace_id);
CREATE INDEX IF NOT EXISTS idx_trace_events_timestamp ON trace_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_trace_events_function_name ON trace_events(function_name);
CREATE INDEX IF NOT EXISTS idx_trace_events_event_type ON trace_events(event_type);
CREATE INDEX IF NOT EXISTS idx_trace_events_module ON trace_events(module_name);

CREATE INDEX IF NOT EXISTS idx_traces_started_at ON traces(started_at);
CREATE INDEX IF NOT EXISTS idx_traces_status ON traces(status);
CREATE INDEX IF NOT EXISTS idx_traces_thread_id ON traces(thread_id);

CREATE INDEX IF NOT EXISTS idx_exceptions_trace_id ON exceptions(trace_id);
CREATE INDEX IF NOT EXISTS idx_exceptions_type ON exceptions(exception_type);
CREATE INDEX IF NOT EXISTS idx_exceptions_event_id ON exceptions(event_id);

CREATE INDEX IF NOT EXISTS idx_variables_event_id ON variables(event_id);
CREATE INDEX IF NOT EXISTS idx_variables_name ON variables(name);

-- Record migration
INSERT INTO _breadcrumb_schema_version (version, description)
VALUES (1, 'Initial schema with traces, events, variables, and exceptions tables')
ON CONFLICT DO NOTHING;
