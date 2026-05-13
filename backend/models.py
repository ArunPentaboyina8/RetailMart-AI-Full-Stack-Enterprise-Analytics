# =============================================================================
# RetailMart AI Analytics Platform - Pydantic Models
# =============================================================================
"""
Request/Response models for the REST API.
Provides type-safe validation for all endpoints.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

# =============================================================================
# Enums
# =============================================================================

class AnalyticsModule(str, Enum):
    SALES = "sales"
    CUSTOMERS = "customers"
    PRODUCTS = "products"
    STORES = "stores"
    OPERATIONS = "operations"
    MARKETING = "marketing"


class AlertSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CLVTier(str, Enum):
    PLATINUM = "Platinum"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"
    BASIC = "Basic"


# =============================================================================
# Request Models
# =============================================================================

class ChatRequest(BaseModel):
    """User question sent to the AI analytics agent."""
    question: str = Field(..., min_length=3, max_length=500, description="Natural language question about the data")
    context: Optional[str] = Field(None, description="Additional context for the question")
    include_sql: bool = Field(False, description="Whether to include the generated SQL in the response")
    include_data: bool = Field(True, description="Whether to include raw data in the response")


class RefreshRequest(BaseModel):
    """Request to refresh materialized views."""
    module: Optional[AnalyticsModule] = Field(None, description="Specific module to refresh, or None for all")
    concurrent: bool = Field(False, description="Use concurrent refresh")


# =============================================================================
# Response Models
# =============================================================================

class HealthResponse(BaseModel):
    """API health check response."""
    status: str
    database: bool
    vector_db: bool
    llm_configured: bool
    timestamp: datetime


class ChatResponse(BaseModel):
    """AI analytics agent response."""
    answer: str = Field(..., description="Natural language answer")
    sql_query: Optional[str] = Field(None, description="Generated SQL query (if requested)")
    data: Optional[list[dict[str, Any]]] = Field(None, description="Query results (if requested)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    sources: list[str] = Field(default_factory=list, description="KPIs/views used")
    tokens_used: Optional[int] = Field(None, description="Total tokens consumed")
    latency_ms: Optional[int] = Field(None, description="Total processing time in ms")
    model_used: str = Field(..., description="LLM model that generated the response")
    cached: bool = Field(False, description="Whether response was from cache")


class ExecutiveSummary(BaseModel):
    """Executive dashboard KPIs."""
    reference_date: Optional[date] = None
    total_orders: Optional[int] = None
    total_customers: Optional[int] = None
    total_revenue: Optional[float] = None
    overall_aov: Optional[float] = None
    orders_today: Optional[int] = None
    revenue_today: Optional[float] = None
    orders_30d: Optional[int] = None
    customers_30d: Optional[int] = None
    revenue_30d: Optional[float] = None
    aov_30d: Optional[float] = None
    revenue_growth_pct: Optional[float] = None
    orders_growth_pct: Optional[float] = None
    avg_daily_revenue: Optional[float] = None
    avg_daily_orders: Optional[float] = None


class AlertItem(BaseModel):
    """Business alert."""
    alert_type: str
    severity: AlertSeverity
    alert_message: str
    recommended_action: str
    entity_name: Optional[str] = None
    metric: Optional[str] = None


class AlertsResponse(BaseModel):
    """All active alerts."""
    total_count: int
    high_count: int
    medium_count: int
    low_count: int
    alerts: list[AlertItem]


class APIResponse(BaseModel):
    """Standard API wrapper response."""
    success: bool = True
    data: Any = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = False


class MonthlyTrend(BaseModel):
    """Monthly sales trend data point."""
    month_key: str
    month_name: str
    year: int
    month: int
    total_orders: int
    unique_customers: int
    gross_revenue: float
    net_revenue: float
    avg_order_value: float
    mom_growth_pct: Optional[float] = None
    yoy_growth_pct: Optional[float] = None
    performance_status: Optional[str] = None


class AIUsageLog(BaseModel):
    """AI operation tracking record."""
    question: str
    model_used: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    estimated_cost_usd: float
    cached: bool
    success: bool
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
