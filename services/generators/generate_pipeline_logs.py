import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path("sample_data/pipeline_logs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "pipeline_logs.csv"

DEFAULT_NUM_RECORDS = 25_000

PIPELINES = [
    "orders-pipeline",
    "payments-pipeline",
    "security-log-ingestion",
    "warehouse-export-job",
    "databricks-bronze-job",
    "databricks-silver-job"
]

REGIONS = [
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "ap-south-1"
]

ERROR_MESSAGES = [
    "schema_mismatch_detected",
    "s3_access_denied",
    "database_connection_timeout",
    "invalid_timestamp_format",
    "negative_amount_threshold_exceeded",
    "job_cluster_startup_failed",
    "missing_required_column",
    "api_token_expired",
    "null_spike_detected",
    "row_count_anomaly_detected"
]


def generate_pipeline_logs(num_records: int = DEFAULT_NUM_RECORDS):
    start_base = datetime(2026, 5, 1, 0, 0, 0)

    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "run_id",
            "pipeline_name",
            "region",
            "status",
            "start_time",
            "end_time",
            "duration_seconds",
            "records_processed",
            "error_message",
            "trigger_type"
        ])

        for i in range(1, num_records + 1):
            pipeline_name = random.choice(PIPELINES)
            region = random.choice(REGIONS)

            start_time = start_base + timedelta(seconds=random.randint(0, 30 * 24 * 60 * 60))
            duration_seconds = random.randint(30, 2400)
            end_time = start_time + timedelta(seconds=duration_seconds)

            status = random.choices(
                ["success", "failed", "warning"],
                weights=[82, 10, 8],
                k=1
            )[0]

            records_processed = random.randint(1_000, 250_000)
            error_message = ""

            if status == "failed":
                error_message = random.choice(ERROR_MESSAGES)
                records_processed = random.randint(0, 50_000)

            if status == "warning":
                error_message = random.choice([
                    "late_arriving_data_detected",
                    "minor_null_spike_detected",
                    "processing_time_above_baseline",
                    "partial_partition_delay"
                ])

            writer.writerow([
                f"RUN{i:09d}",
                pipeline_name,
                region,
                status,
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                duration_seconds,
                records_processed,
                error_message,
                random.choice(["scheduled", "manual", "file_arrival", "api_trigger"])
            ])

    print(f"Generated {num_records} pipeline logs at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_pipeline_logs()