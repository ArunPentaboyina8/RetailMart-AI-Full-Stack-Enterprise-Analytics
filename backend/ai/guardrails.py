# =============================================================================
# RetailMart AI Analytics - SQL Guardrails
# =============================================================================
"""
Safety layer to validate AI-generated SQL queries before execution.
Prevents SQL injection, destructive operations, and excessive queries.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Forbidden SQL keywords — anything that modifies data
FORBIDDEN_KEYWORDS = [
    r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b',
    r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b', r'\bGRANT\b',
    r'\bREVOKE\b', r'\bEXEC\b', r'\bEXECUTE\b', r'\bCALL\b',
    r'\bCOPY\b', r'\bLOAD\b', r'\bIMPORT\b',
    r'\bSET\s+ROLE\b', r'\bSET\s+SESSION\b',
    r'\bREFRESH\b',  # Prevent MV refresh via AI
]

# Forbidden patterns — SQL injection vectors
FORBIDDEN_PATTERNS = [
    r';\s*(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE)',  # Stacked queries
    r'--',           # SQL comments (can hide malicious code)
    r'/\*.*\*/',     # Block comments
    r"'\s*OR\s+'",   # Classic SQL injection
    r"'\s*OR\s+1\s*=\s*1",
    r'UNION\s+ALL\s+SELECT.*FROM\s+pg_',  # System table access
    r'pg_catalog\.',  # System catalog access
    r'information_schema\.',  # Schema snooping (we control this separately)
    r'pg_sleep',      # DoS via sleep
    r'dblink',        # External connections
    r'lo_import',     # Large object manipulation
    r'pg_read_file',  # File system access
    r'pg_ls_dir',     # Directory listing
]

# Allowed schemas — queries can only touch these
ALLOWED_SCHEMAS = [
    'analytics',
    'sales',
    'customers',
    'products',
    'stores',
    'marketing',
    'core',
]

# Maximum query complexity thresholds
MAX_JOINS = 8
MAX_SUBQUERIES = 5
MAX_QUERY_LENGTH = 3000  # characters


class SQLValidationError(Exception):
    """Raised when SQL validation fails."""
    def __init__(self, message: str, violation_type: str):
        self.message = message
        self.violation_type = violation_type
        super().__init__(self.message)


class SQLGuardrails:
    """Validates AI-generated SQL for safety and compliance."""

    @staticmethod
    def validate(sql: str) -> tuple[bool, Optional[str]]:
        """
        Validate SQL query. Returns (is_valid, error_message).
        If is_valid is True, error_message is None.
        """
        try:
            SQLGuardrails._check_not_empty(sql)
            SQLGuardrails._check_length(sql)
            SQLGuardrails._check_is_select(sql)
            SQLGuardrails._check_forbidden_keywords(sql)
            SQLGuardrails._check_forbidden_patterns(sql)
            SQLGuardrails._check_complexity(sql)
            SQLGuardrails._check_has_limit(sql)
            return True, None
        except SQLValidationError as e:
            logger.warning(f"SQL validation failed [{e.violation_type}]: {e.message}")
            return False, e.message

    @staticmethod
    def sanitize(sql: str) -> str:
        """
        Attempt to sanitize SQL by adding safety measures.
        Returns sanitized SQL or raises if unsalvageable.
        """
        sql = sql.strip()

        # Remove trailing semicolons (prevent stacked queries)
        sql = sql.rstrip(';')

        # Remove SQL comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

        # Add LIMIT if missing
        if not re.search(r'\bLIMIT\b', sql, re.IGNORECASE):
            sql = sql + '\nLIMIT 50'

        return sql.strip()

    @staticmethod
    def _check_not_empty(sql: str):
        if not sql or not sql.strip():
            raise SQLValidationError("Empty SQL query", "EMPTY")

    @staticmethod
    def _check_length(sql: str):
        if len(sql) > MAX_QUERY_LENGTH:
            raise SQLValidationError(
                f"Query exceeds maximum length ({len(sql)} > {MAX_QUERY_LENGTH} chars)",
                "LENGTH"
            )

    @staticmethod
    def _check_is_select(sql: str):
        """Ensure the query starts with SELECT or WITH (CTE)."""
        normalized = sql.strip().upper()
        if not (normalized.startswith('SELECT') or normalized.startswith('WITH')):
            raise SQLValidationError(
                "Only SELECT queries are allowed. Query must start with SELECT or WITH.",
                "NOT_SELECT"
            )

    @staticmethod
    def _check_forbidden_keywords(sql: str):
        upper_sql = sql.upper()
        for pattern in FORBIDDEN_KEYWORDS:
            if re.search(pattern, upper_sql):
                keyword = re.search(pattern, upper_sql).group()
                raise SQLValidationError(
                    f"Forbidden SQL keyword detected: {keyword}. Only SELECT queries are allowed.",
                    "FORBIDDEN_KEYWORD"
                )

    @staticmethod
    def _check_forbidden_patterns(sql: str):
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE | re.DOTALL):
                raise SQLValidationError(
                    f"Potentially unsafe SQL pattern detected. Query rejected for security.",
                    "INJECTION_RISK"
                )

    @staticmethod
    def _check_complexity(sql: str):
        upper_sql = sql.upper()

        # Count JOINs
        join_count = len(re.findall(r'\bJOIN\b', upper_sql))
        if join_count > MAX_JOINS:
            raise SQLValidationError(
                f"Query too complex: {join_count} JOINs (max {MAX_JOINS})",
                "COMPLEXITY"
            )

        # Count subqueries
        subquery_count = upper_sql.count('(SELECT')
        if subquery_count > MAX_SUBQUERIES:
            raise SQLValidationError(
                f"Query too complex: {subquery_count} subqueries (max {MAX_SUBQUERIES})",
                "COMPLEXITY"
            )

    @staticmethod
    def _check_has_limit(sql: str):
        """Warn if no LIMIT clause (we'll add one during sanitization)."""
        if not re.search(r'\bLIMIT\b', sql, re.IGNORECASE):
            logger.info("Query missing LIMIT clause — will be added during sanitization")


def validate_and_sanitize(sql: str) -> tuple[str, Optional[str]]:
    """
    Combined validate + sanitize pipeline.
    Returns (sanitized_sql, error_message).
    If error_message is not None, the SQL was rejected.
    """
    # First sanitize
    try:
        sanitized = SQLGuardrails.sanitize(sql)
    except Exception as e:
        return "", f"Failed to sanitize SQL: {str(e)}"

    # Then validate
    is_valid, error = SQLGuardrails.validate(sanitized)
    if not is_valid:
        return "", error

    return sanitized, None
