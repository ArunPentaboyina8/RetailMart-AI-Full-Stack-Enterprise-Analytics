# =============================================================================
# RetailMart AI Analytics Platform - FastAPI Application
# =============================================================================
"""
Main application entry point. Serves REST API endpoints for the dashboard
and an AI chat endpoint for natural language analytics queries.

Run with: uvicorn main:app --reload --port 8000
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from ai.agent import ask_analytics
from ai.rag import get_knowledge_stats, is_knowledge_loaded, load_knowledge_base
from config import get_settings
from database import (
    close_db_pool,
    execute_query,
    execute_query_single,
    init_db_pool,
    test_connection,
)
from models import (
    AlertItem,
    AlertsResponse,
    APIResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
)
from monitoring.tracker import AIUsageTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Application Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    settings = get_settings()
    logger.info("=" * 60)
    logger.info("  RetailMart AI Analytics Platform - Starting")
    logger.info("=" * 60)

    # Initialize database pool
    try:
        init_db_pool()
        db_ok = test_connection()
        logger.info(f"Database connection: {'✓ Connected' if db_ok else '✗ Failed'}")
    except Exception as e:
        logger.warning(f"Database not available: {e} (API will work without DB)")

    # Initialize knowledge base
    try:
        doc_count = load_knowledge_base()
        logger.info(f"Knowledge base: ✓ {doc_count} documents loaded")
    except Exception as e:
        logger.warning(f"Knowledge base init failed: {e}")

    logger.info(f"AI Model: {settings.gemini_model}")
    logger.info(f"Fallback Model: {settings.fallback_model}")
    logger.info(f"Environment: {settings.app_env}")
    logger.info("=" * 60)
    logger.info(f"  API ready at http://{settings.app_host}:{settings.app_port}")
    logger.info(f"  Docs at http://{settings.app_host}:{settings.app_port}/docs")
    logger.info("=" * 60)

    yield

    # Shutdown
    close_db_pool()
    logger.info("Application shutdown complete")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="RetailMart AI Analytics Platform",
    description=(
        "Enterprise analytics platform with AI-powered natural language querying. "
        "Built with FastAPI, LangChain/LangGraph, ChromaDB, and PostgreSQL."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Middleware — Request Timing
# =============================================================================

@app.middleware("http")
async def add_timing_header(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    response.headers["X-Response-Time-Ms"] = str(duration)
    return response


# =============================================================================
# Health & Status Endpoints
# =============================================================================

@app.get("/", tags=["Status"])
async def root():
    """API root — basic info."""
    return {
        "name": "RetailMart AI Analytics Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Health check endpoint for Docker / load balancers."""
    settings = get_settings()
    db_ok = False
    try:
        db_ok = test_connection()
    except Exception:
        pass

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        database=db_ok,
        vector_db=is_knowledge_loaded(),
        llm_configured=bool(settings.gemini_api_key),
        timestamp=datetime.utcnow(),
    )


# =============================================================================
# AI Chat Endpoint
# =============================================================================

@app.post("/api/chat", response_model=ChatResponse, tags=["AI Chat"])
async def chat(request: ChatRequest):
    """
    Ask a natural language question about the retail data.

    The AI agent will:
    1. Classify your intent
    2. Retrieve relevant KPI context (RAG)
    3. Generate and validate a SQL query
    4. Execute it against PostgreSQL
    5. Synthesize a business-friendly answer

    Example questions:
    - "What was our total revenue last month?"
    - "Who are our top 5 customers by lifetime value?"
    - "Which categories have the highest return rates?"
    - "How is our delivery SLA trending?"
    """
    settings = get_settings()

    # Budget check
    within_budget, remaining = AIUsageTracker.check_budget(settings.max_daily_cost_usd)
    if not within_budget:
        raise HTTPException(
            status_code=429,
            detail=f"Daily AI budget exhausted (${settings.max_daily_cost_usd}). Resets at midnight UTC."
        )

    try:
        result = await ask_analytics(
            question=request.question,
            include_sql=request.include_sql,
            include_data=request.include_data,
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Analytics REST API Endpoints
# =============================================================================

@app.get("/api/executive-summary", tags=["Sales"])
async def get_executive_summary():
    """Get executive dashboard KPIs."""
    try:
        data = execute_query_single("SELECT * FROM analytics.mv_executive_summary;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/sales/monthly-trend", tags=["Sales"])
async def get_monthly_trend(limit: int = Query(12, ge=1, le=36)):
    """Get monthly sales trend."""
    try:
        data = execute_query(
            "SELECT * FROM analytics.mv_monthly_sales_dashboard ORDER BY year DESC, month DESC LIMIT %s;",
            (limit,)
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/sales/daily-trend", tags=["Sales"])
async def get_daily_trend():
    """Get last 30 days daily sales."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_recent_sales_trend;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/sales/payment-modes", tags=["Sales"])
async def get_payment_modes():
    """Get revenue by payment method."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_sales_by_payment_mode;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/sales/quarterly", tags=["Sales"])
async def get_quarterly_sales():
    """Get quarterly sales with growth metrics."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_quarterly_sales LIMIT 8;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/sales/day-of-week", tags=["Sales"])
async def get_day_of_week():
    """Get sales by day of week."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_sales_by_dayofweek;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


# --- Customers ---

@app.get("/api/customers/top", tags=["Customers"])
async def get_top_customers(limit: int = Query(20, ge=1, le=100)):
    """Get top customers by lifetime value."""
    try:
        data = execute_query(
            """SELECT cust_id, full_name, city, state, clv_tier, total_orders,
                      total_revenue, avg_order_value, days_since_last_order, customer_status
               FROM analytics.mv_customer_lifetime_value
               WHERE total_orders > 0
               ORDER BY total_revenue DESC LIMIT %s;""",
            (limit,)
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/customers/clv-tiers", tags=["Customers"])
async def get_clv_tiers():
    """Get CLV tier distribution."""
    try:
        data = execute_query(
            """SELECT clv_tier, COUNT(*) as customer_count,
                      ROUND(SUM(total_revenue)::NUMERIC, 2) as total_revenue,
                      ROUND(AVG(total_revenue)::NUMERIC, 2) as avg_revenue
               FROM analytics.mv_customer_lifetime_value
               WHERE total_orders > 0
               GROUP BY clv_tier ORDER BY avg_revenue DESC;"""
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/customers/rfm-segments", tags=["Customers"])
async def get_rfm_segments():
    """Get RFM segment distribution."""
    try:
        data = execute_query(
            """SELECT rfm_segment, COUNT(*) as customer_count,
                      ROUND(SUM(total_spent)::NUMERIC, 2) as total_revenue,
                      ROUND(AVG(recency_days)::NUMERIC, 0) as avg_recency,
                      ROUND(AVG(order_count)::NUMERIC, 1) as avg_frequency,
                      MAX(recommended_action) as recommended_action
               FROM analytics.mv_rfm_analysis
               GROUP BY rfm_segment ORDER BY total_revenue DESC;"""
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/customers/churn-risk", tags=["Customers"])
async def get_churn_risk(limit: int = Query(20, ge=1, le=50)):
    """Get high-priority churn risk customers."""
    try:
        data = execute_query(
            "SELECT * FROM analytics.vw_churn_risk_customers WHERE priority_score >= 5 LIMIT %s;",
            (limit,)
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


# --- Products ---

@app.get("/api/products/top", tags=["Products"])
async def get_top_products(limit: int = Query(20, ge=1, le=100)):
    """Get top products by revenue."""
    try:
        data = execute_query(
            "SELECT * FROM analytics.mv_top_products ORDER BY revenue_rank LIMIT %s;",
            (limit,)
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/products/categories", tags=["Products"])
async def get_categories():
    """Get category performance."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_category_performance;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/products/abc-analysis", tags=["Products"])
async def get_abc_analysis():
    """Get ABC analysis summary."""
    try:
        data = execute_query(
            """SELECT abc_classification, COUNT(*) as product_count,
                      ROUND(SUM(net_revenue)::NUMERIC, 2) as total_revenue,
                      ROUND((SUM(net_revenue) / SUM(SUM(net_revenue)) OVER () * 100)::NUMERIC, 2) as pct
               FROM analytics.mv_abc_analysis
               GROUP BY abc_classification ORDER BY abc_classification;"""
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/products/inventory", tags=["Products"])
async def get_inventory_status():
    """Get inventory status summary."""
    try:
        data = execute_query(
            """SELECT stock_status, COUNT(*) as product_count,
                      ROUND((COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100), 2) as pct
               FROM analytics.vw_inventory_turnover
               GROUP BY stock_status;"""
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


# --- Stores ---

@app.get("/api/stores/performance", tags=["Stores"])
async def get_store_performance(limit: int = Query(20, ge=1, le=50)):
    """Get store performance rankings."""
    try:
        data = execute_query(
            "SELECT * FROM analytics.mv_store_performance ORDER BY revenue_rank LIMIT %s;",
            (limit,)
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/stores/regional", tags=["Stores"])
async def get_regional_performance():
    """Get regional performance."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_regional_performance;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


# --- Operations ---

@app.get("/api/operations/summary", tags=["Operations"])
async def get_operations_summary():
    """Get operations summary KPIs."""
    try:
        data = execute_query_single("SELECT * FROM analytics.mv_operations_summary;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/operations/delivery", tags=["Operations"])
async def get_delivery_performance():
    """Get monthly delivery performance."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_delivery_performance LIMIT 12;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/operations/couriers", tags=["Operations"])
async def get_courier_comparison():
    """Get courier performance comparison."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_courier_comparison;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/operations/returns", tags=["Operations"])
async def get_return_analysis():
    """Get return analysis by category and reason."""
    try:
        data = execute_query(
            """SELECT category, SUM(return_count) as total_returns,
                      ROUND(SUM(total_refunds)::NUMERIC, 2) as total_refunds,
                      ROUND(AVG(return_rate_pct)::NUMERIC, 2) as avg_return_rate
               FROM analytics.vw_return_analysis
               GROUP BY category ORDER BY total_returns DESC;"""
        )
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


# --- Marketing ---

@app.get("/api/marketing/campaigns", tags=["Marketing"])
async def get_campaigns():
    """Get campaign performance."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_campaign_performance LIMIT 20;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


@app.get("/api/marketing/channels", tags=["Marketing"])
async def get_channels():
    """Get channel performance."""
    try:
        data = execute_query("SELECT * FROM analytics.vw_channel_performance;")
        return APIResponse(data=data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))


# --- Alerts ---

@app.get("/api/alerts", tags=["Alerts"])
async def get_alerts(limit: int = Query(50, ge=1, le=200)):
    """Get all active business alerts."""
    try:
        alerts = execute_query(
            "SELECT * FROM analytics.vw_all_active_alerts LIMIT %s;", (limit,)
        )

        high = sum(1 for a in alerts if a.get("severity") == "HIGH")
        medium = sum(1 for a in alerts if a.get("severity") == "MEDIUM")
        low = sum(1 for a in alerts if a.get("severity") == "LOW")

        return AlertsResponse(
            total_count=len(alerts),
            high_count=high,
            medium_count=medium,
            low_count=low,
            alerts=[AlertItem(**a) for a in alerts],
        )
    except Exception as e:
        return APIResponse(success=False, error=str(e))


# =============================================================================
# AI Monitoring Endpoints
# =============================================================================

@app.get("/api/ai/stats", tags=["AI Monitoring"])
async def get_ai_stats():
    """Get AI usage statistics — tokens, costs, latency, errors."""
    return APIResponse(data=AIUsageTracker.get_stats())


@app.get("/api/ai/recent", tags=["AI Monitoring"])
async def get_ai_recent(limit: int = Query(20, ge=1, le=100)):
    """Get recent AI operation records."""
    return APIResponse(data=AIUsageTracker.get_recent_records(limit))


@app.get("/api/ai/knowledge", tags=["AI Monitoring"])
async def get_knowledge_info():
    """Get knowledge base statistics."""
    return APIResponse(data=get_knowledge_stats())


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
