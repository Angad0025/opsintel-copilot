import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()

OUTPUT_DIR = Path("sample_data/warehouse_exports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "warehouse_exports.csv"

DEFAULT_NUM_RECORDS = 5_000

EXPORT_TYPES = [
    "scheduled_report",
    "manual_csv_export",
    "api_extract",
    "dashboard_download",
    "bulk_table_export"
]

DATASETS = [
    "orders_curated",
    "payments_curated",
    "customer_profiles",
    "security_alerts",
    "incident_timelines",
    "warehouse_finance_export"
]

USERS = [
    "analyst@datacorp.com",
    "admin@datacorp.com",
    "finance@datacorp.com",
    "service_account@datacorp.com",
    "security@datacorp.com",
    "external_vendor@datacorp.com"
]

REGIONS = [
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "ap-south-1"
]


def generate_warehouse_exports(num_records: int = DEFAULT_NUM_RECORDS):
    start_time = datetime(2026, 5, 1, 0, 0, 0)

    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "export_id",
            "export_type",
            "dataset_name",
            "user_email",
            "region",
            "export_time",
            "rows_exported",
            "file_size_mb",
            "destination",
            "status",
            "risk_level"
        ])

        for i in range(1, num_records + 1):
            export_type = random.choice(EXPORT_TYPES)
            dataset_name = random.choice(DATASETS)
            user_email = random.choice(USERS)
            rows_exported = random.randint(100, 250_000)
            file_size_mb = round(random.uniform(1, 500), 2)
            status = random.choices(
                ["success", "failed", "blocked"],
                weights=[85, 10, 5],
                k=1
            )[0]

            risk_level = "low"

            if export_type == "bulk_table_export" or rows_exported > 100_000 or file_size_mb > 250:
                risk_level = random.choice(["medium", "high", "critical"])

            if user_email == "external_vendor@datacorp.com":
                risk_level = random.choice(["medium", "high", "critical"])

            if status in ["failed", "blocked"]:
                risk_level = random.choice(["medium", "high"])

            writer.writerow([
                f"EXP{i:09d}",
                export_type,
                dataset_name,
                user_email,
                random.choice(REGIONS),
                (start_time + timedelta(seconds=random.randint(0, 30 * 24 * 60 * 60))).strftime("%Y-%m-%d %H:%M:%S"),
                rows_exported,
                file_size_mb,
                random.choice(["s3_export_bucket", "external_sftp", "email_attachment", "bi_dashboard", "api_client"]),
                status,
                risk_level
            ])

    print(f"Generated {num_records} warehouse export events at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_warehouse_exports()