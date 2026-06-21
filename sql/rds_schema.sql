-- =============================================================
-- OpsIntel Copilot — RDS PostgreSQL Schema
-- Database: opsintel
-- =============================================================

-- Drop tables if they exist (safe to re-run)
DROP TABLE IF EXISTS rag_query_history CASCADE;
DROP TABLE IF EXISTS data_quality_results CASCADE;
DROP TABLE IF EXISTS correlations CASCADE;
DROP TABLE IF EXISTS security_alerts CASCADE;
DROP TABLE IF EXISTS incident_summary CASCADE;

-- =============================================================
-- 1. security_alerts
-- Mirrors gold_security_alerts from Databricks
-- =============================================================
CREATE TABLE security_alerts (
    event_id            VARCHAR(255) PRIMARY KEY,
    event_type          VARCHAR(100) NOT NULL,
    user_email          VARCHAR(255),
    source_ip           VARCHAR(50),
    region               VARCHAR(100),
    event_time          TIMESTAMP NOT NULL,
    success             BOOLEAN,
    is_brute_force      BOOLEAN DEFAULT FALSE,
    is_escalation       BOOLEAN DEFAULT FALSE,
    is_impossible_travel BOOLEAN DEFAULT FALSE,
    is_large_export     BOOLEAN DEFAULT FALSE,
    is_token_rotation   BOOLEAN DEFAULT FALSE,
    alert_generated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- 2. correlations
-- Mirrors gold_correlation_records from Databricks
-- (sourced from PySpark correlation_records table)
-- =============================================================
CREATE TABLE correlations (
    correlation_id       VARCHAR(255) PRIMARY KEY,
    correlation_type     VARCHAR(100),
    pipeline_run_id      VARCHAR(255),
    pipeline_name        VARCHAR(255),
    pipeline_failed_at   TIMESTAMP,
    error_message        TEXT,
    security_event_id    VARCHAR(255),
    security_event_type  VARCHAR(100),
    security_event_at    TIMESTAMP,
    involved_user        VARCHAR(255),
    time_diff_minutes    DOUBLE PRECISION,
    confidence_score     DECIMAL(4,2),
    recommendation       TEXT,
    correlated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- 3. incident_summary
-- Mirrors gold_incident_summary from Databricks
-- Composite primary key: each hour can have multiple regions
-- =============================================================
CREATE TABLE incident_summary (
    incident_hour            TIMESTAMP NOT NULL,
    region                   VARCHAR(100) NOT NULL,
    total_events             INTEGER DEFAULT 0,
    brute_force_count        INTEGER DEFAULT 0,
    escalation_count         INTEGER DEFAULT 0,
    impossible_travel_count  INTEGER DEFAULT 0,
    large_export_count       INTEGER DEFAULT 0,
    summary_generated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (incident_hour, region)
);

-- =============================================================
-- 4. data_quality_results
-- Mirrors gold_data_quality_results from Databricks
-- =============================================================
CREATE TABLE data_quality_results (
    order_id        VARCHAR(255) PRIMARY KEY,
    amount          DECIMAL(18,2),
    currency        VARCHAR(10),
    created_at      TIMESTAMP,
    quality_flag    VARCHAR(50),
    checked_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================
-- 5. rag_query_history
-- Stores every question asked to the investigation copilot
-- =============================================================
CREATE TABLE rag_query_history (
    id              SERIAL PRIMARY KEY,
    question        TEXT NOT NULL,
    answer          TEXT,
    sources_used    TEXT,
    asked_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER
);

-- =============================================================
-- Indexes for fast API queries
-- =============================================================
CREATE INDEX idx_security_alerts_event_time ON security_alerts(event_time DESC);
CREATE INDEX idx_security_alerts_event_type ON security_alerts(event_type);
CREATE INDEX idx_security_alerts_user_email ON security_alerts(user_email);

CREATE INDEX idx_correlations_confidence ON correlations(confidence_score DESC);
CREATE INDEX idx_correlations_involved_user ON correlations(involved_user);
CREATE INDEX idx_correlations_correlated_at ON correlations(correlated_at DESC);
CREATE INDEX idx_correlations_type ON correlations(correlation_type);

CREATE INDEX idx_incident_summary_hour ON incident_summary(incident_hour DESC);
CREATE INDEX idx_incident_summary_region ON incident_summary(region);

CREATE INDEX idx_data_quality_flag ON data_quality_results(quality_flag);
CREATE INDEX idx_data_quality_created_at ON data_quality_results(created_at DESC);

CREATE INDEX idx_rag_history_asked_at ON rag_query_history(asked_at DESC);

-- =============================================================
-- Confirmation
-- =============================================================
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_name = t.table_name 
     AND table_schema = 'public') AS column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;