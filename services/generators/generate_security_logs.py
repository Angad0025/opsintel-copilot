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
    "role_assumed",
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
    rows = []

    # ── Normal activity ───────────────────────────────────────────
    for i in range(1, num_records + 1):
        event_type = random.choice(EVENT_TYPES)
        event_time = start_time + timedelta(
            seconds=random.randint(0, 30 * 24 * 60 * 60)
        )
        success = "true"
        risk_score = random.randint(1, 40)

        if event_type in ["login_failure", "mfa_failure", "permission_denied"]:
            success = "false"
            risk_score = random.randint(50, 95)

        rows.append([
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

    # ── Scenario 1: Brute Force ───────────────────────────────────
    brute_start = datetime(2026, 5, 15, 2, 0, 0)
    target_user = "admin@datacorp.com"
    target_ip = fake.ipv4_public()
    for j in range(50):
        rows.append([
            f"BRUTE{j:06d}",
            "brute_force",
            target_user,
            target_ip,
            "us-east-1",
            (brute_start + timedelta(seconds=j * 12)).strftime("%Y-%m-%d %H:%M:%S"),
            "false",
            random.randint(88, 100),
            "unknown"
        ])

    # ── Scenario 2: Impossible Travel ────────────────────────────
    travel_user = "engineer@datacorp.com"
    travel_time_1 = datetime(2026, 5, 20, 3, 0, 0)
    travel_time_2 = travel_time_1 + timedelta(minutes=30)

    rows.append([
        "TRAVEL000001",
        "impossible_travel",
        travel_user,
        fake.ipv4_public(),
        "us-east-1",
        travel_time_1.strftime("%Y-%m-%d %H:%M:%S"),
        "true",
        95,
        "laptop"
    ])
    rows.append([
        "TRAVEL000002",
        "impossible_travel",
        travel_user,
        fake.ipv4_public(),
        "ap-south-1",
        travel_time_2.strftime("%Y-%m-%d %H:%M:%S"),
        "true",
        95,
        "mobile"
    ])

    # ── Scenario 3: Privilege Escalation ─────────────────────────
    escalation_time = datetime(2026, 5, 22, 2, 5, 0)
    rows.append([
        "ESCL000001",
        "privilege_escalation",
        "analyst@datacorp.com",
        fake.ipv4_public(),
        "us-east-1",
        escalation_time.strftime("%Y-%m-%d %H:%M:%S"),
        "true",
        92,
        "desktop"
    ])

    # ── Scenario 4: Large Data Export ────────────────────────────
    export_time = datetime(2026, 5, 22, 3, 0, 0)
    rows.append([
        "EXPORT000001",
        "large_data_export",
        "service_account@datacorp.com",
        fake.ipv4_public(),
        "us-west-2",
        export_time.strftime("%Y-%m-%d %H:%M:%S"),
        "true",
        88,
        "server"
    ])

    # ── Scenario 5: API Token Rotation ───────────────────────────
    token_time = escalation_time + timedelta(minutes=5)
    rows.append([
        "TOKEN000001",
        "api_token_rotation",
        "analyst@datacorp.com",
        fake.ipv4_public(),
        "us-east-1",
        token_time.strftime("%Y-%m-%d %H:%M:%S"),
        "true",
        75,
        "desktop"
    ])

    # ── Scenario 6: Config Change ─────────────────────────────────
    config_time = datetime(2026, 5, 22, 2, 7, 0)
    rows.append([
        "CONFIG000001",
        "config_change",
        "admin@datacorp.com",
        fake.ipv4_public(),
        "us-east-1",
        config_time.strftime("%Y-%m-%d %H:%M:%S"),
        "true",
        70,
        "laptop"
    ])

    # ── Write all rows ────────────────────────────────────────────
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
        writer.writerows(rows)

    print(f"Generated {len(rows)} security logs at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_security_logs()