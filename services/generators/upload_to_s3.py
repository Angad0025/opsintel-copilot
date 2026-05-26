from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

S3_BUCKET_NAME = "opsintel-copilot-angad-0025"

FILES_TO_UPLOAD = [
    {
        "local_path": "sample_data/orders/orders.csv",
        "s3_key": "raw/orders/orders.csv"
    },
    {
        "local_path": "sample_data/security_logs/security_logs.csv",
        "s3_key": "raw/security_logs/security_logs.csv"
    },
    {
        "local_path": "sample_data/admin_events/admin_events.csv",
        "s3_key": "raw/admin_events/admin_events.csv"
    },
    {
        "local_path": "sample_data/pipeline_logs/pipeline_logs.csv",
        "s3_key": "raw/pipeline_logs/pipeline_logs.csv"
    },
    {
        "local_path": "sample_data/api_token_events/api_token_events.csv",
        "s3_key": "raw/api_token_events/api_token_events.csv"
    },
    {
        "local_path": "sample_data/warehouse_exports/warehouse_exports.csv",
        "s3_key": "raw/warehouse_exports/warehouse_exports.csv"
    },
    {
        "local_path": "sample_data/playbooks/api_token_failure_runbook.md",
        "s3_key": "rag-docs/playbooks/api_token_failure_runbook.md"
    },
    {
        "local_path": "sample_data/playbooks/schema_drift_runbook.md",
        "s3_key": "rag-docs/playbooks/schema_drift_runbook.md"
    },
    {
        "local_path": "sample_data/playbooks/suspicious_export_playbook.md",
        "s3_key": "rag-docs/playbooks/suspicious_export_playbook.md"
    },
    {
        "local_path": "sample_data/playbooks/data_quality_runbook.md",
        "s3_key": "rag-docs/playbooks/data_quality_runbook.md"
    },
    {
        "local_path": "sample_data/playbooks/pipeline_failure_runbook.md",
        "s3_key": "rag-docs/playbooks/pipeline_failure_runbook.md"
    },
]


def upload_file(s3_client, local_path: str, s3_key: str):
    file_path = Path(local_path)

    if not file_path.exists():
        print(f"SKIPPED: File not found: {local_path}")
        return

    try:
        s3_client.upload_file(str(file_path), S3_BUCKET_NAME, s3_key)
        print(f"UPLOADED: {local_path} -> s3://{S3_BUCKET_NAME}/{s3_key}")
    except ClientError as error:
        print(f"FAILED: {local_path}")
        print(error)


def main():
    print("Starting upload to S3...")
    print(f"Target bucket: s3://{S3_BUCKET_NAME}")

    try:
        s3_client = boto3.client("s3")
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
    except NoCredentialsError:
        print("FAILED: AWS credentials not found. Run 'aws configure' first.")
        return
    except ClientError as error:
        print("FAILED: Could not access S3 bucket.")
        print(error)
        return

    for file_info in FILES_TO_UPLOAD:
        upload_file(
            s3_client=s3_client,
            local_path=file_info["local_path"],
            s3_key=file_info["s3_key"]
        )

    print("S3 upload complete.")


if __name__ == "__main__":
    main()