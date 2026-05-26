import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()

OUTPUT_DIR = Path("sample_data/orders")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "orders.csv"

DEFAULT_NUM_RECORDS = 100_000

SERVICES = [
    "orders-api",
    "payments-api",
    "inventory-service",
    "checkout-service",
    "pricing-service",
    "shipment-service"
]

REGIONS = [
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "ap-south-1"
]

STATUSES = [
    "created",
    "paid",
    "failed",
    "cancelled",
    "refunded"
]

CURRENCIES = [
    "USD",
    "EUR",
    "GBP",
    "INR"
]


def generate_orders(num_records: int = DEFAULT_NUM_RECORDS):
    start_time = datetime(2026, 5, 1, 0, 0, 0)

    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "order_id",
            "customer_id",
            "service_name",
            "order_status",
            "amount",
            "currency",
            "region",
            "created_at",
            "updated_at",
            "payment_method",
            "is_priority_order"
        ])

        for i in range(1, num_records + 1):
            created_at = start_time + timedelta(seconds=random.randint(0, 30 * 24 * 60 * 60))
            updated_at = created_at + timedelta(minutes=random.randint(1, 180))

            amount = round(random.uniform(5, 1200), 2)

            # Inject bad records for future data-quality checks
            if random.random() < 0.02:
                amount = -amount

            writer.writerow([
                f"ORD{i:09d}",
                f"CUST{random.randint(1, 50000):07d}",
                random.choice(SERVICES),
                random.choice(STATUSES),
                amount,
                random.choice(CURRENCIES),
                random.choice(REGIONS),
                created_at.strftime("%Y-%m-%d %H:%M:%S"),
                updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                random.choice(["credit_card", "debit_card", "paypal", "apple_pay", "bank_transfer"]),
                random.choice(["true", "false"])
            ])

    print(f"Generated {num_records} orders at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_orders()