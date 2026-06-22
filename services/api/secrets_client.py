# =============================================================
# OpsIntel Copilot — Secrets Client
# Fetches all credentials from AWS Secrets Manager
# FastAPI never has hardcoded passwords — everything comes here
# =============================================================

import boto3
import json
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


def get_secret(secret_name: str) -> dict:
    """
    Fetch a secret from AWS Secrets Manager.
    Returns the secret as a dictionary.
    """
    try:
        client = boto3.client("secretsmanager", region_name="us-east-1")
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except Exception as e:
        logger.error(f"Failed to fetch secret {secret_name}: {e}")
        raise


@lru_cache(maxsize=None)
def get_rds_credentials() -> dict:
    """
    Returns RDS connection details.
    Cached after first call — no repeated Secrets Manager calls.
    """
    return get_secret("opsintel/rds/credentials")


@lru_cache(maxsize=None)
def get_databricks_config() -> dict:
    """
    Returns Databricks host and token.
    """
    return get_secret("opsintel/databricks/token")


@lru_cache(maxsize=None)
def get_bedrock_config() -> dict:
    """
    Returns Bedrock region config.
    """
    return get_secret("opsintel/bedrock/api_key")