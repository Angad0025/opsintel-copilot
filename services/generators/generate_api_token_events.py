import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()

OUTPUT_DIR = Path("sample_data/api_token_events")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "api_token_events.csv"

DEFAULT_NUM_RECORDS = 5_000

TOKEN_EVENTS = [
    "token_created",
    "token_rotated",
    "token_expired",
    "token_revoked",
    "token_used",
    "token_failed_auth"
]

SERVICES = [
    "orders-pipeline",
    "payments-pipeline",
    "security-log-ingestion",
    "warehouse-export-job",
    "databricks-bronze-job",
    "databricks-silver-job",
    "fastapi-backend"
]

USERS = [
    "admin@datacorp.com",
    "devops@datacorp.com",
    "platform-lead@datacorp.com",
    "service_account@datacorp.com",
    "security-admin@datacorp.com"
]

REGIONS = [
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "ap-south-1"
]


def generate_api_token_events(num_records: int = DEFAULT_NUM_RECORDS):
    start_time = datetime(2026, 5, 1, 0, 0, 0)

    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "token_event_id",
            "token_id",
            "event_type",
            "service_name",
            "user_email",
            "region",
            "event_time",
            "source_ip",
            "risk_level",
            "status"
        ])

        for i in range(1, num_records + 1):
            event_type = random.choice(TOKEN_EVENTS)

            risk_level = "low"
            status = "success"

            if event_type in ["token_expired", "token_failed_auth", "token_revoked"]:
                risk_level = random.choice(["medium", "high", "critical"])
                status = random.choice(["failed", "blocked", "expired"])

            writer.writerow([
                f"TOKEVT{i:09d}",
                f"TOKEN{random.randint(1, 1500):07d}",
                event_type,
                random.choice(SERVICES),
                random.choice(USERS),
                random.choice(REGIONS),
                (start_time + timedelta(seconds=random.randint(0, 30 * 24 * 60 * 60))).strftime("%Y-%m-%d %H:%M:%S"),
                fake.ipv4_public(),
                risk_level,
                status
            ])

    print(f"Generated {num_records} API token events at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_api_token_events()