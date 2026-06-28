cat > ~/Desktop/opsintel-copilot/docs/dbt_setup.md << 'EOF'
# dbt Setup Guide

## Prerequisites
- Databricks workspace on AWS
- SQL warehouse created in Databricks
- Python 3.11+

## Installation

```bash
pip install dbt-databricks
pip install elementary-data
```

## Configuration

Create `dbt/profiles.yml`:

```yaml
opsintel:
  target: dev
  outputs:
    dev:
      type: databricks
      host: dbc-f7dc29ce-1820.cloud.databricks.com
      http_path: /sql/1.0/warehouses/YOUR_WAREHOUSE_HTTP_PATH
      token: "{{ env_var('DBT_DATABRICKS_TOKEN') }}"
      schema: opsintel_copilot
      catalog: workspace
```

## Running dbt

```bash
cd dbt

# Install packages (Elementary + dbt_utils)
dbt deps

# Test connection
dbt debug

# Check source freshness
dbt source freshness

# Run all models
dbt run

# Run specific layers
dbt run --select staging.*
dbt run --select silver.*
dbt run --select gold.*

# Run all tests
dbt test

# Run snapshots (SCD Type 2)
dbt snapshot

# Generate documentation
dbt docs generate
dbt docs serve

# Run Elementary observability
edr monitor
```

## Model Layers

| Layer | Materialization | Purpose |
|-------|----------------|---------|
| staging | view | Type casting and column renaming only |
| silver | table | Business logic, macro validation, suspicious event flagging |
| gold | table | Incident summary, security alerts, correlations, quality |
| snapshots | table | SCD Type 2 for incident and alert lifecycle |

## Custom Macros

- `is_valid_timestamp(column)` — checks column is not null, >= 2020-01-01, <= current timestamp
- `is_valid_currency(column)` — checks currency is in [USD, EUR, GBP, JPY, CAD]
- `flag_suspicious_event(event_col, event_type)` — returns boolean flag for suspicious events

## Custom Tests

- `assert_no_impossible_travel` — fails if user appears in 2+ locations within 1 hour
- `assert_row_count_not_dropped` — fails if model row count drops below threshold

## CI/CD

GitHub Actions runs on every PR touching `dbt/**`:
1. `dbt deps` — install packages
2. `dbt compile` — validate SQL
3. SQLFluff lint — enforce SQL style
4. `dbt test` — run all tests
EOF