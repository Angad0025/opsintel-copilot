# =============================================================
# OpsIntel Copilot — Bedrock RAG Client
# Queries Amazon Bedrock Knowledge Base for RAG answers
# =============================================================

import boto3
import logging
import time

logger = logging.getLogger(__name__)

# Knowledge Base ID — set after creating the KB in AWS console
KNOWLEDGE_BASE_ID = "YOUR_KNOWLEDGE_BASE_ID"
MODEL_ARN = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"


def get_bedrock_agent_client():
    return boto3.client("bedrock-agent-runtime", region_name="us-east-1")


def query_knowledge_base(question: str) -> dict:
    """
    Send a question to Bedrock Knowledge Base.
    Returns the answer and source citations.
    """
    start_time = time.time()

    try:
        client = get_bedrock_agent_client()
        response = client.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 5
                        }
                    }
                }
            }
        )

        answer = response["output"]["text"]
        citations = response.get("citations", [])
        sources = []
        for citation in citations:
            for ref in citation.get("retrievedReferences", []):
                location = ref.get("location", {})
                if "s3Location" in location:
                    sources.append(location["s3Location"].get("uri", ""))

        response_time_ms = int((time.time() - start_time) * 1000)

        return {
            "answer": answer,
            "sources": sources,
            "response_time_ms": response_time_ms
        }

    except Exception as e:
        logger.error(f"Bedrock query failed: {e}")
        return {
            "answer": f"I was unable to find an answer. Error: {str(e)}",
            "sources": [],
            "response_time_ms": int((time.time() - start_time) * 1000)
        }