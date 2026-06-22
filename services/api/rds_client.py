# =============================================================
# OpsIntel Copilot — RDS Client
# All PostgreSQL queries for FastAPI endpoints
# =============================================================

import psycopg2
import psycopg2.extras
import logging
from services.api.secrets_client import get_rds_credentials

logger = logging.getLogger(__name__)


def get_connection():
    creds = get_rds_credentials()
    return psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        database=creds["database"],
        user=creds["username"],
        password=creds["password"],
        connect_timeout=10
    )


def fetch_security_alerts(limit: int = 100, severity: str = None) -> list:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        if severity:
            cur.execute("""
                SELECT * FROM security_alerts
                WHERE event_type = %s
                ORDER BY event_time DESC
                LIMIT %s
            """, (severity, limit))
        else:
            cur.execute("""
                SELECT * FROM security_alerts
                ORDER BY event_time DESC
                LIMIT %s
            """, (limit,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def fetch_correlations(limit: int = 100, correlation_type: str = None) -> list:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        if correlation_type:
            cur.execute("""
                SELECT * FROM correlations
                WHERE correlation_type = %s
                ORDER BY confidence_score DESC
                LIMIT %s
            """, (correlation_type, limit))
        else:
            cur.execute("""
                SELECT * FROM correlations
                ORDER BY confidence_score DESC
                LIMIT %s
            """, (limit,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def fetch_incident_summary(limit: int = 100) -> list:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT * FROM incident_summary
            ORDER BY incident_hour DESC
            LIMIT %s
        """, (limit,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def fetch_data_quality(limit: int = 100, flag: str = None) -> list:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        if flag:
            cur.execute("""
                SELECT * FROM data_quality_results
                WHERE quality_flag = %s
                ORDER BY checked_at DESC
                LIMIT %s
            """, (flag, limit))
        else:
            cur.execute("""
                SELECT * FROM data_quality_results
                ORDER BY checked_at DESC
                LIMIT %s
            """, (limit,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def save_rag_query(question: str, answer: str, sources: str, response_time_ms: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO rag_query_history (question, answer, sources_used, response_time_ms)
            VALUES (%s, %s, %s, %s)
        """, (question, answer, sources, response_time_ms))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def fetch_rag_history(limit: int = 20) -> list:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT * FROM rag_query_history
            ORDER BY asked_at DESC
            LIMIT %s
        """, (limit,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()