-- ============================================
-- Jiri TimescaleDB Initialization Script
-- ============================================
-- This script runs on first container startup

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Enable UUID extension for user IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Interaction Logs (Time-Series)
-- ============================================
-- Stores every voice interaction for analytics and debugging

CREATE TABLE IF NOT EXISTS interaction_logs (
    id BIGSERIAL,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    intent VARCHAR(100),
    tool_called VARCHAR(100),
    input_text TEXT,
    result_summary TEXT,
    latency_ms INTEGER,
    success_score DOUBLE PRECISION,
    trace_id VARCHAR(64),
    PRIMARY KEY (id, time)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('interaction_logs', 'time', if_not_exists => TRUE);

-- Index for fast user lookups
CREATE INDEX IF NOT EXISTS idx_interaction_logs_user_id 
    ON interaction_logs (user_id, time DESC);

-- Index for session lookups
CREATE INDEX IF NOT EXISTS idx_interaction_logs_session_id 
    ON interaction_logs (session_id, time DESC);

-- ============================================
-- Tool Registry (Cache for discovered MCPs)
-- ============================================

CREATE TABLE IF NOT EXISTS tool_registry (
    tool_name VARCHAR(100) PRIMARY KEY,
    mcp_manifest_url TEXT NOT NULL,
    description TEXT,
    capabilities JSONB,
    last_discovered TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0
);

-- ============================================
-- User Preferences (For RAG augmentation)
-- ============================================

CREATE TABLE IF NOT EXISTS user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 1.0,
    source VARCHAR(50),  -- 'explicit', 'inferred', 'feedback'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, preference_key)
);

-- Index for fast preference lookups
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id 
    ON user_preferences (user_id);

-- ============================================
-- Grant permissions
-- ============================================
-- The POSTGRES_USER from env will own these tables
