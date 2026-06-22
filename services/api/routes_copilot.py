# =============================================================
# OpsIntel Copilot — RAG Copilot Routes
# =============================================================

from fastapi import APIRouter
from pydantic import BaseModel
from services.api.bedrock_client import query_knowledge_base
from services.api.rds_client import save_rag_query, fetch_rag_history

router = APIRouter()


class CopilotQuestion(BaseModel):
    question: str


@router.post("/copilot/ask")
def ask_copilot(body: CopilotQuestion):
    """
    Ask the investigation copilot a natural language question.
    Routes to Bedrock Knowledge Base for RAG-grounded answer.
    """
    result = query_knowledge_base(body.question)

    save_rag_query(
        question=body.question,
        answer=result["answer"],
        sources=", ".join(result["sources"]),
        response_time_ms=result["response_time_ms"]
    )

    return {
        "question": body.question,
        "answer": result["answer"],
        "sources": result["sources"],
        "response_time_ms": result["response_time_ms"]
    }


@router.get("/copilot/history")
def get_copilot_history(limit: int = 20):
    """Returns recent copilot questions and answers."""
    data = fetch_rag_history(limit=limit)
    return {
        "count": len(data),
        "history": data
    }