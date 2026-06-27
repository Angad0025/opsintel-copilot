# =============================================================
# OpsIntel Copilot — Bedrock RAG Client
# Queries Amazon Bedrock Managed Knowledge Base for RAG answers
# =============================================================

import boto3
import json
import logging
import time

logger = logging.getLogger(__name__)

KNOWLEDGE_BASE_ID = "ZMTLLFQNTO"
MODEL_ID = "us.anthropic.claude-sonnet-4-6"


def get_bedrock_agent_client():
    return boto3.client("bedrock-agent-runtime", region_name="us-east-1")


def get_bedrock_runtime_client():
    return boto3.client("bedrock-runtime", region_name="us-east-1")


def query_knowledge_base(question: str) -> dict:
    """
    Send a question to Bedrock Managed Knowledge Base.
    Step 1: Retrieve relevant chunks from KB
    Step 2: Send chunks + question to Claude for answer generation
    """
    start_time = time.time()

    try:
        # Step 1 — Retrieve relevant context from Managed Knowledge Base
        agent_client = get_bedrock_agent_client()
        retrieve_response = agent_client.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={"text": question}
        )

        # Extract retrieved chunks and sources
        results = retrieve_response.get("retrievalResults", [])
        context_chunks = []
        sources = []

        for result in results:
            content = result.get("content", {}).get("text", "")
            if content:
                context_chunks.append(content)
            location = result.get("location", {})
            if "s3Location" in location:
                sources.append(location["s3Location"].get("uri", ""))

        context = "\n\n---\n\n".join(context_chunks)

        if not context:
            return {
                "answer": "I could not find relevant information in the knowledge base for this question.",
                "sources": [],
                "response_time_ms": int((time.time() - start_time) * 1000)
            }

        # Step 2 — Generate answer using Claude with retrieved context
        runtime_client = get_bedrock_runtime_client()

        prompt = f"""You are an AI investigation copilot for OpsIntel, a data reliability and security platform.

Use the following context from our incident records, correlation data, and security playbooks to answer the question.
Only use information from the provided context. If the context doesn't contain enough information, say so clearly.

CONTEXT:
{context}

QUESTION: {question}

Provide a clear, specific answer based on the evidence in the context above."""

        response = runtime_client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response["body"].read())
        answer = response_body["content"][0]["text"]
        response_time_ms = int((time.time() - start_time) * 1000)

        return {
            "answer": answer,
            "sources": list(set(sources)),
            "response_time_ms": response_time_ms
        }

    except Exception as e:
        logger.error(f"Bedrock query failed: {e}")
        return {
            "answer": f"I was unable to find an answer. Error: {str(e)}",
            "sources": [],
            "response_time_ms": int((time.time() - start_time) * 1000)
        }