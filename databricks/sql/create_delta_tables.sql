-- ============================================================
-- OpsIntel Copilot
-- Week 3 — Delta Table SQL Validation
--
-- Purpose:
-- Validate bronze and silver Delta tables created by Databricks
-- PySpark notebooks.
--
-- Database:
-- opsintel_copilot
-- ============================================================

CREATE DATABASE IF NOT EXISTS opsintel_copilot;

USE opsintel_copilot;


-- ============================================================
-- Bronze table checks
-- ============================================================

SELECT
    'bronze_orders' AS table_name,
    COUNT(*) AS record_count
FROM bronze_orders

UNION ALL

SELECT
    'bronze_security_logs' AS table_name,
    COUNT(*) AS record_count
FROM bronze_security_logs

UNION ALL

SELECT
    'bronze_admin_events' AS table_name,
    COUNT(*) AS record_count
FROM bronze_admin_events;


-- ============================================================
-- Silver table checks
-- ============================================================

SELECT
    'silver_orders' AS table_name,
    COUNT(*) AS record_count
FROM silver_orders

UNION ALL

SELECT
    'silver_security_logs' AS table_name,
    COUNT(*) AS record_count
FROM silver_security_logs

UNION ALL

SELECT
    'silver_admin_events' AS table_name,
    COUNT(*) AS record_count
FROM silver_admin_events;


-- ============================================================
-- Bronze vs Silver comparison
-- ============================================================

SELECT
    'orders' AS dataset_name,
    (SELECT COUNT(*) FROM bronze_orders) AS bronze_count,
    (SELECT COUNT(*) FROM silver_orders) AS silver_count,
    (SELECT COUNT(*) FROM bronze_orders) - (SELECT COUNT(*) FROM silver_orders) AS records_removed

UNION ALL

SELECT
    'security_logs' AS dataset_name,
    (SELECT COUNT(*) FROM bronze_security_logs) AS bronze_count,
    (SELECT COUNT(*) FROM silver_security_logs) AS silver_count,
    (SELECT COUNT(*) FROM bronze_security_logs) - (SELECT COUNT(*) FROM silver_security_logs) AS records_removed

UNION ALL

SELECT
    'admin_events' AS dataset_name,
    (SELECT COUNT(*) FROM bronze_admin_events) AS bronze_count,
    (SELECT COUNT(*) FROM silver_admin_events) AS silver_count,
    (SELECT COUNT(*) FROM bronze_admin_events) - (SELECT COUNT(*) FROM silver_admin_events) AS records_removed;


-- ============================================================
-- Bad records summary
-- ============================================================

SELECT
    dataset_name,
    rule_failed,
    bad_record_count,
    summary_created_at
FROM bad_records_summary
ORDER BY dataset_name, rule_failed;


-- ============================================================
-- Sample bronze records
-- ============================================================

SELECT *
FROM bronze_orders
LIMIT 10;

SELECT *
FROM bronze_security_logs
LIMIT 10;

SELECT *
FROM bronze_admin_events
LIMIT 10;


-- ============================================================
-- Sample silver records
-- ============================================================

SELECT *
FROM silver_orders
LIMIT 10;

SELECT *
FROM silver_security_logs
LIMIT 10;

SELECT *
FROM silver_admin_events
LIMIT 10;


-- ============================================================
-- Ingestion metadata check
-- ============================================================

SELECT
    _dataset_name,
    COUNT(*) AS record_count,
    MIN(_ingestion_timestamp) AS first_ingested_at,
    MAX(_ingestion_timestamp) AS last_ingested_at,
    COUNT(DISTINCT _source_file) AS source_file_count
FROM bronze_orders
GROUP BY _dataset_name

UNION ALL

SELECT
    _dataset_name,
    COUNT(*) AS record_count,
    MIN(_ingestion_timestamp) AS first_ingested_at,
    MAX(_ingestion_timestamp) AS last_ingested_at,
    COUNT(DISTINCT _source_file) AS source_file_count
FROM bronze_security_logs
GROUP BY _dataset_name

UNION ALL

SELECT
    _dataset_name,
    COUNT(*) AS record_count,
    MIN(_ingestion_timestamp) AS first_ingested_at,
    MAX(_ingestion_timestamp) AS last_ingested_at,
    COUNT(DISTINCT _source_file) AS source_file_count
FROM bronze_admin_events
GROUP BY _dataset_name;