# Schema Drift Runbook

## Purpose

This runbook helps investigate pipeline failures caused by unexpected schema changes in raw data.

## Common Symptoms

- Pipeline fails with schema_mismatch_detected
- Pipeline fails with missing_required_column
- Bronze ingestion succeeds but silver validation fails
- Null values spike in required columns
- Record count drops unexpectedly

## Investigation Steps

1. Identify the failed pipeline from pipeline_logs.
2. Check whether the error message indicates schema_mismatch_detected or missing_required_column.
3. Compare the raw file schema with the expected schema.
4. Check recent admin_events for config_changed or databricks_job_modified.
5. Check whether the upstream service changed its export format.
6. Review bad records and rejected rows.
7. Validate timestamps, required fields, and data types.
8. Update schema mapping only after confirming the change is expected.

## Severity Guidance

Critical severity if:
- Required production fields are missing
- Multiple downstream tables are affected
- Gold reporting tables are stale or incorrect

Medium severity if:
- Schema change affects optional fields
- Bad record percentage is low
- Downstream reporting is not impacted

## Recommended Remediation

- Quarantine malformed records
- Update schema enforcement logic
- Notify upstream data owner
- Add schema drift alerting
- Reprocess affected partitions after correction