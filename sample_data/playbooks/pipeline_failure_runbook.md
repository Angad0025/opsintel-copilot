# Pipeline Failure Investigation Runbook

## Purpose

This runbook helps investigate failed or degraded data pipeline runs across Databricks jobs, ingestion pipelines, transformation jobs, and warehouse export workflows.

## Common Symptoms

- Pipeline status is failed or warning
- Error message contains database_connection_timeout
- Error message contains s3_access_denied
- Error message contains api_token_expired
- Error message contains schema_mismatch_detected
- Error message contains missing_required_column
- Records processed are much lower than expected
- Job duration is much higher than baseline
- Downstream silver or gold tables are stale

## Investigation Steps

1. Identify the failed pipeline run from pipeline_logs.
2. Capture the pipeline_name, region, start_time, end_time, status, records_processed, and error_message.
3. Check whether the failure is caused by access, schema, token, data quality, or infrastructure.
4. If error_message is api_token_expired, search api_token_events for token_expired, token_revoked, token_rotated, or token_failed_auth events near the failure time.
5. If error_message is s3_access_denied, search admin_events for iam_policy_updated, s3_bucket_policy_updated, permission_added, or permission_removed events near the failure time.
6. If error_message is schema_mismatch_detected or missing_required_column, compare raw input schema with expected schema and check schema drift runbook.
7. If records_processed is unusually low, check raw data arrival, row count baseline, and data quality runbook.
8. Search security_logs for high-risk login_failure, mfa_failure, or role_assumed events involving admin or service accounts near the failure time.
9. Search warehouse_exports for suspicious export events if the failed pipeline relates to warehouse-export-job or curated datasets.
10. Build an incident timeline using all related evidence within a 30-minute window.
11. Assign severity based on production impact, affected datasets, security context, and downstream reporting impact.
12. Re-run the pipeline only after root cause is understood or mitigated.

## Severity Guidance

Critical severity if:
- Production gold tables are stale or incorrect
- Multiple downstream dashboards or consumers are affected
- Failure follows suspicious admin or security activity
- Failure involves access control, token revocation, or external data export
- Business-critical pipeline such as orders-pipeline or payments-pipeline fails

Medium severity if:
- One pipeline fails but downstream outputs are not affected
- Pipeline can be safely retried
- Issue is limited to bronze or raw layer
- No suspicious security activity is detected

Low severity if:
- Pipeline warning does not impact data freshness
- Failure occurred in non-production or test scenario
- Issue is expected and already documented

## Recommended Remediation

- Retry transient infrastructure failures after checking logs
- Refresh or rotate expired tokens
- Restore correct IAM/S3 permissions
- Quarantine malformed records
- Notify upstream data producers for schema changes
- Update Databricks job configuration if needed
- Reprocess affected partitions
- Create an incident summary for RAG investigation history