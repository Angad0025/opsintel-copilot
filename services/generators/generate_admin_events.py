import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()

OUTPUT_DIR = Path("sample_data/admin_events")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "admin_events.csv"

DEFAULT_NUM_RECORDS = 10_000

ADMIN_USERS = [
    "admin@datacorp.com",
    "platform-lead@datacorp.com",
    "security-admin@datacorp.com",
    "devops@datacorp.com",
    "service-owner@datacorp.com"
]

ACTIONS = [
    "config_changed",
    "iam_policy_updated",
    "pipeline_schedule_changed",
    "databricks_job_modified",
    "s3_bucket_policy_updated",
    "secret_rotated",
    "permission_added",
    "permission_removed",
    "deployment_triggered"
]

TARGET_SERVICES = [
    "orders-pipeline",
    "payments-pipeline",
    "security-log-ingestion",
    "warehouse-export-job",
    "databricks-bronze-job",
    "databricks-silver-job",
    "fastapi-backend",
    "streamlit-dashboard"
]

REGIONS = [
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "ap-south-1"
]


def generate_admin_events(num_records: int = DEFAULT_NUM_RECORDS):
    start_time = datetime(2026, 5, 1, 0, 0, 0)

    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "admin_event_id",
            "admin_user",
            "action",
            "target_service",
            "region",
            "event_time",
            "change_summary",
            "risk_level",
            "source_ip"
        ])

        for i in range(1, num_records + 1):
            action = random.choice(ACTIONS)

            risk_level = random.choice(["low", "medium", "high"])

            if action in [
                "iam_policy_updated",
                "s3_bucket_policy_updated",
                "secret_rotated",
                "permission_added"
            ]:
                risk_level = random.choice(["medium", "high", "critical"])

            event_time = start_time + timedelta(seconds=random.randint(0, 30 * 24 * 60 * 60))

            writer.writerow([
                f"ADM{i:09d}",
                random.choice(ADMIN_USERS),
                action,
                random.choice(TARGET_SERVICES),
                random.choice(REGIONS),
                event_time.strftime("%Y-%m-%d %H:%M:%S"),
                f"{action} performed on production service",
                risk_level,
                fake.ipv4_public()
            ])

    print(f"Generated {num_records} admin events at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_admin_events()