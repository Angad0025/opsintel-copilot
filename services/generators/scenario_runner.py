from generate_orders import generate_orders
from generate_security_logs import generate_security_logs
from generate_admin_events import generate_admin_events
from generate_pipeline_logs import generate_pipeline_logs
from generate_api_token_events import generate_api_token_events
from generate_warehouse_exports import generate_warehouse_exports


def run_large_scenario():
    print("Starting OpsIntel large synthetic data generation...")

    generate_orders(num_records=100_000)
    generate_security_logs(num_records=100_000)
    generate_admin_events(num_records=10_000)
    generate_pipeline_logs(num_records=25_000)
    generate_api_token_events(num_records=5_000)
    generate_warehouse_exports(num_records=5_000)

    print("Large synthetic data generation complete.")
    print("Generated datasets:")
    print("- sample_data/orders/orders.csv")
    print("- sample_data/security_logs/security_logs.csv")
    print("- sample_data/admin_events/admin_events.csv")
    print("- sample_data/pipeline_logs/pipeline_logs.csv")
    print("- sample_data/api_token_events/api_token_events.csv")
    print("- sample_data/warehouse_exports/warehouse_exports.csv")


if __name__ == "__main__":
    run_large_scenario()