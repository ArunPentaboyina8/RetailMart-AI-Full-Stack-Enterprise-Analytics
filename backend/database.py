# =============================================================================
# RetailMart AI Analytics Platform - Database Connection
# =============================================================================
"""
PostgreSQL connection management using psycopg2 connection pool.
Provides both sync (for FastAPI endpoints) and read-only (for AI agent) access.
"""

import psycopg2
from psycopg2 import pool, extras
from contextlib import contextmanager
from typing import Any, Optional
from config import get_settings
import logging

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool: Optional[pool.ThreadedConnectionPool] = None


def init_db_pool(min_conn: int = 2, max_conn: int = 10) -> None:
    """Initialize the database connection pool."""
    global _connection_pool
    settings = get_settings()

    try:
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=min_conn,
            maxconn=max_conn,
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
        )
        logger.info(
            f"Database pool initialized: {settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise


def close_db_pool() -> None:
    """Close all connections in the pool."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        logger.info("Database pool closed")


@contextmanager
def get_db_connection():
    """Get a database connection from the pool (context manager)."""
    conn = None
    try:
        conn = _connection_pool.getconn()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            _connection_pool.putconn(conn)


def execute_query(query: str, params: tuple = None) -> list[dict]:
    """
    Execute a SELECT query and return results as list of dicts.
    Used by REST API endpoints.
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            return [dict(row) for row in results]


def execute_query_single(query: str, params: tuple = None) -> Optional[dict]:
    """Execute a query and return a single result row."""
    results = execute_query(query, params)
    return results[0] if results else None


def execute_readonly_query(query: str, params: tuple = None) -> list[dict]:
    """
    Execute a READ-ONLY query. Used by the AI agent.
    Sets the transaction to read-only for safety.
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("SET TRANSACTION READ ONLY;")
            cur.execute(query, params)
            results = cur.fetchall()
            conn.rollback()  # rollback the read-only transaction
            return [dict(row) for row in results]


def get_table_schema(schema_name: str = "analytics") -> list[dict]:
    """Get schema information for knowledge base embedding."""
    query = """
        SELECT 
            table_schema, table_name, column_name, 
            data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = %s
        ORDER BY table_name, ordinal_position;
    """
    return execute_query(query, (schema_name,))


def get_kpi_metadata() -> list[dict]:
    """Get all KPI metadata for embedding into vector store."""
    query = """
        SELECT 
            kpi_name, kpi_category, kpi_type, object_name,
            description, business_question, formula, 
            source_tables, refresh_frequency
        FROM analytics.kpi_metadata
        WHERE is_active = TRUE
        ORDER BY kpi_category, kpi_name;
    """
    return execute_query(query)


def test_connection() -> bool:
    """Test database connectivity."""
    try:
        result = execute_query_single("SELECT 1 as ok")
        return result is not None and result.get("ok") == 1
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
