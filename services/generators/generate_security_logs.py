import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()

OUTPUT_DIR = Path("sample_data/security_logs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "security_logs.csv"

DEFAULT_NUM_RECORDS = 100_000

EVENT_TYPES = [
    "login_success",
    "login_failure",
    "password_reset",
    "mfa_challenge",
    "mfa_failure",
    "permission_denied",
    "role_assumed"
]

USERS = [
    "admin@datacorp.com",
    "analyst@datacorp.com",
    "engineer@datacorp.com",
    "service_account@datacorp.com",
    "security@datacorp.com",
    "platform@datacorp.com"
]

REGIONS = [
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "ap-south-1"
]


def generate_security_logs(num_records: int = DEFAULT_NUM_RECORDS):
    start_time = datetime(2026, 5, 1, 0, 0, 0)

    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "event_id",
            "event_type",
            "user_email",
            "source_ip",
            "region",
            "event_time",
            "success",
            "risk_score",
            "device_type"
        ])

        for i in range(1, num_records + 1):
            event_type = random.choice(EVENT_TYPES)
            event_time = start_time + timedelta(seconds=random.randint(0, 30 * 24 * 60 * 60))

            success = "true"
            risk_score = random.randint(1, 40)

            if event_type in ["login_failure", "mfa_failure", "permission_denied"]:
                success = "false"
                risk_score = random.randint(50, 95)

            # Inject suspicious high-risk login failures
            if random.random() < 0.03:
                event_type = "login_failure"
                success = "false"
                risk_score = random.randint(85, 100)

            writer.writerow([
                f"SEC{i:09d}",
                event_type,
                random.choice(USERS),
                fake.ipv4_public(),
                random.choice(REGIONS),
                event_time.strftime("%Y-%m-%d %H:%M:%S"),
                success,
                risk_score,
                random.choice(["laptop", "desktop", "mobile", "server", "unknown"])
            ])

    print(f"Generated {num_records} security logs at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_security_logs()