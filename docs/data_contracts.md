cat > ~/Desktop/opsintel-copilot/docs/data_contracts.md << 'EOF'
# Data Contracts

## What Are Data Contracts

Data contracts are formal YAML agreements between data producers and consumers. They define schema, data types, SLAs, ownership, and quality rules. They make implicit assumptions explicit and enforceable.

## Where They Live
contracts/

├── orders_contract.yml

├── security_logs_contract.yml

└── admin_events_contract.yml
## Contract Structure

Each contract defines:

- `domain` — which business domain owns this data
- `owner` — team responsible for this data
- `version` — contract version for change management
- `sla` — freshness, availability, and row count requirements
- `schema` — field definitions with types, constraints, and allowed values

## Enforcement

Contracts are enforced at two levels:

**1. Generator level** — `upload_to_s3.py` validates each generated file against its contract before uploading to S3. If validation fails, the file is rejected and the pipeline does not proceed.

**2. dbt level** — `sources.yml` declares freshness thresholds matching the contract SLAs. `schema.yml` tests enforce not_null, unique, and accepted_values rules matching the contract schema.

## Adding a New Contract

1. Create `contracts/your_domain_contract.yml`
2. Add freshness check to `dbt/models/sources.yml`
3. Add schema tests to `dbt/models/schema.yml`
4. Update `upload_to_s3.py` to validate against the new contract
5. Add a test in `tests/test_data_contracts.py`

## Why This Matters

Data contracts are the hottest topic in data engineering right now. They shift data quality left — catching problems at the producer before they corrupt downstream tables. Without contracts, schema changes silently break pipelines. With contracts, breaking changes are caught immediately at the source.
EOF