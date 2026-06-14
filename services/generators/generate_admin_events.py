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
    rows = []

    # ── Normal admin activity ─────────────────────────────────────
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

        event_time = start_time + timedelta(
            seconds=random.randint(0, 30 * 24 * 60 * 60)
        )

        rows.append([
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

    # ── Scenario 1: Config change right before pipeline failure ───
    # Correlation engine will link this to the pipeline failure
    failure_time = datetime(2026, 5, 22, 2, 7, 0)
    for j in range(3):
        rows.append([
            f"CRITICAL{j:06d}",
            "admin@datacorp.com",
            "config_changed",
            "orders-pipeline",
            "us-east-1",
            (failure_time + timedelta(minutes=j)).strftime("%Y-%m-%d %H:%M:%S"),
            "critical config change performed on production orders pipeline",
            "critical",
            fake.ipv4_public()
        ])

    # ── Scenario 2: Privilege escalation ──────────────────────────
    # Analyst suddenly gets admin access they shouldn't have
    escalation_time = datetime(2026, 5, 22, 2, 5, 0)
    rows.append([
        "PRIV000001",
        "analyst@datacorp.com",
        "permission_added",
        "databricks-bronze-job",
        "us-east-1",
        escalation_time.strftime("%Y-%m-%d %H:%M:%S"),
        "admin privileges granted unexpectedly to analyst account",
        "critical",
        fake.ipv4_public()
    ])

    # ── Scenario 3: Secret rotation after suspicious activity ─────
    # Secrets rotated right after the privilege escalation
    secret_time = escalation_time + timedelta(minutes=3)
    rows.append([
        "SECRET000001",
        "security-admin@datacorp.com",
        "secret_rotated",
        "fastapi-backend",
        "us-east-1",
        secret_time.strftime("%Y-%m-%d %H:%M:%S"),
        "emergency secret rotation triggered after privilege escalation",
        "high",
        fake.ipv4_public()
    ])

    # ── Write all rows ────────────────────────────────────────────
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
        writer.writerows(rows)

    print(f"Generated {len(rows)} admin events at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_admin_events()