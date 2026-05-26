# Data Quality Incident Runbook

## Purpose

This runbook helps investigate data quality incidents in cloud data pipelines, including invalid values, duplicate records, null spikes, row count anomalies, freshness failures, and bad record ratio increases.

## Common Symptoms

- Orders contain negative amount values
- Required fields contain unexpected null values
- Duplicate order_id values appear in raw or bronze data
- Row count is much lower or higher than normal
- Pipeline processes fewer records than expected
- Freshness checks fail because new data did not arrive on time
- Bad record percentage crosses the expected threshold
- Silver validation fails after bronze ingestion succeeds

## Investigation Steps

1. Identify the failed or warning pipeline run from pipeline_logs.
2. Check the pipeline_name, start_time, status, records_processed, and error_message.
3. Compare current row count against historical baseline.
4. Check raw orders data for invalid values such as negative amount.
5. Check for duplicate primary keys such as duplicate order_id.
6. Check whether required columns contain null or empty values.
7. Check whether timestamps are valid and within expected date ranges.
8. Search admin_events for config_changed or databricks_job_modified events before the issue.
9. Search security_logs for unusual admin or service account activity near the failure time.
10. Quarantine bad records before loading trusted silver or gold tables.

## Severity Guidance

Critical severity if:
- Invalid records affect production reporting
- Gold tables or dashboards are incorrect
- Bad record ratio is above 5%
- Required business fields are missing
- Multiple downstream consumers are affected

Medium severity if:
- Bad records are isolated to one source
- Issue affects only bronze or raw layers
- Downstream gold tables are not impacted

Low severity if:
- Bad records are expected test records
- Issue is below alert threshold
- Data can be safely quarantined

## Recommended Remediation

- Quarantine invalid records
- Add schema and value validation checks
- Notify upstream data producer
- Reprocess affected partitions after correction
- Add monitoring for null spikes, duplicates, freshness, and row count anomaly
- Update Databricks data quality rules if the business logic changed