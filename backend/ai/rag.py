# =============================================================================
# RetailMart AI Analytics - RAG Pipeline
# =============================================================================
"""
Retrieval-Augmented Generation pipeline using ChromaDB.
Embeds KPI definitions, schema context, and business rules
so the LLM has accurate context when generating SQL.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import get_settings

logger = logging.getLogger(__name__)

# Global ChromaDB client
_chroma_client: Optional[chromadb.ClientAPI] = None
_collection: Optional[chromadb.Collection] = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create ChromaDB persistent client."""
    global _chroma_client
    if _chroma_client is None:
        settings = get_settings()
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        _chroma_client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info(f"ChromaDB initialized at {persist_dir}")

    return _chroma_client


def get_collection() -> chromadb.Collection:
    """Get or create the knowledge collection."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        settings = get_settings()
        _collection = client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"description": "RetailMart analytics knowledge base"},
        )
        logger.info(
            f"ChromaDB collection '{settings.chroma_collection_name}' ready "
            f"({_collection.count()} documents)"
        )
    return _collection


def is_knowledge_loaded() -> bool:
    """Check if the knowledge base has been populated."""
    try:
        collection = get_collection()
        return collection.count() > 0
    except Exception:
        return False


# =============================================================================
# Knowledge Base Content
# =============================================================================

# KPI definitions embedded directly — no external DB dependency needed
KPI_KNOWLEDGE = [
    # --- Sales ---
    {
        "id": "kpi_daily_sales",
        "category": "Sales",
        "content": "Daily Sales Summary (analytics.vw_daily_sales_summary): Shows daily gross revenue, net revenue, total orders, unique customers, avg order value, day-over-day growth %, and 7-day moving average. Filters to Delivered orders only. Use for daily trend analysis.",
    },
    {
        "id": "kpi_monthly_sales",
        "category": "Sales",
        "content": "Monthly Sales Dashboard (analytics.mv_monthly_sales_dashboard): Pre-computed monthly metrics including gross_revenue, net_revenue, total_orders, unique_customers, new_customers, returning_customers, avg_order_value. Includes MoM growth (mom_growth_pct), YoY growth (yoy_growth_pct), YTD revenue, 3-month and 6-month moving averages, and performance_status (Strong Growth/Growing/Stable/Declining). Use month_key (YYYY-MM) for filtering.",
    },
    {
        "id": "kpi_executive_summary",
        "category": "Sales",
        "content": "Executive Summary (analytics.mv_executive_summary): Single-row materialized view with top-level KPIs. Contains total_revenue, total_orders, total_customers, overall_aov (all-time), revenue_30d, orders_30d, customers_30d, aov_30d (last 30 days), revenue_growth_pct, orders_growth_pct (vs previous 30 days), avg_daily_revenue, avg_daily_orders. Best for executive dashboard cards.",
    },
    {
        "id": "kpi_payment_modes",
        "category": "Sales",
        "content": "Payment Mode Analysis (analytics.vw_sales_by_payment_mode): Revenue and transactions by payment method (Credit Card, Debit Card, UPI, Net Banking, Cash on Delivery, etc.). Shows pct_of_revenue, pct_of_transactions, and revenue_rank per mode.",
    },
    {
        "id": "kpi_quarterly",
        "category": "Sales",
        "content": "Quarterly Sales (analytics.vw_quarterly_sales): Quarterly aggregation with quarter_label (Q1 2025), total_revenue, total_orders, QoQ growth (qoq_growth_pct), and YoY growth (yoy_growth_pct).",
    },
    {
        "id": "kpi_day_of_week",
        "category": "Sales",
        "content": "Sales by Day of Week (analytics.vw_sales_by_dayofweek): Performance by weekday (Mon-Sun) with is_weekend flag, avg_daily_revenue, variance_from_avg_pct, and revenue_rank. Great for resource planning.",
    },
    # --- Customers ---
    {
        "id": "kpi_clv",
        "category": "Customers",
        "content": "Customer Lifetime Value (analytics.mv_customer_lifetime_value): Comprehensive customer profile with total_orders, total_revenue, avg_order_value, days_since_last_order, loyalty_points, review_count, avg_rating_given, projected_annual_value, clv_tier (Platinum ≥15000, Gold ≥8000, Silver ≥3000, Bronze ≥1000, Basic), customer_status (Active/At Risk/Churning/Churned), age_group.",
    },
    {
        "id": "kpi_rfm",
        "category": "Customers",
        "content": "RFM Analysis (analytics.mv_rfm_analysis): Recency-Frequency-Monetary segmentation. Each dimension scored 1-5 using NTILE. Segments: Champions (R≥4,F≥4,M≥4), Loyal Customers, Recent Customers, Big Spenders, At Risk - High Value (R≤2,F≥4,M≥4), At Risk, Hibernating, Lost, Potential Loyalists. Includes recommended_action per segment.",
    },
    {
        "id": "kpi_cohort",
        "category": "Customers",
        "content": "Cohort Retention (analytics.mv_cohort_retention): Monthly cohort analysis. Tracks retention_rate across months (month_number 0-12). cohort_month is when the customer first purchased. cohort_size is initial size. retained_customers is how many came back.",
    },
    {
        "id": "kpi_churn",
        "category": "Customers",
        "content": "Churn Risk (analytics.vw_churn_risk_customers): High-value customers at risk of churning. Shows churn_risk_level (Churned/High Risk/Medium Risk/Low Risk), priority_score (higher = more urgent, max 10), and recommended_action. Filters to customers inactive >30 days.",
    },
    # --- Products ---
    {
        "id": "kpi_top_products",
        "category": "Products",
        "content": "Top Products (analytics.mv_top_products): All products ranked by net_revenue. Includes prod_name, category, brand, times_ordered, total_units_sold, gross_revenue, net_revenue, avg_rating, current_stock, revenue_rank, units_rank, category_rank, pct_of_total_revenue.",
    },
    {
        "id": "kpi_abc",
        "category": "Products",
        "content": "ABC Analysis (analytics.mv_abc_analysis): Pareto classification. A = top 80% revenue products, B = next 15%, C = bottom 5%. Includes cumulative_pct and revenue_rank.",
    },
    {
        "id": "kpi_categories",
        "category": "Products",
        "content": "Category Performance (analytics.vw_category_performance): Category-level metrics with product_count, order_count, units_sold, net_revenue, avg_price, avg_rating, market_share_pct, revenue_rank.",
    },
    {
        "id": "kpi_inventory",
        "category": "Products",
        "content": "Inventory Turnover (analytics.vw_inventory_turnover): Stock velocity with current_stock, units_sold_30d, daily_velocity, days_of_inventory, stock_status (Out of Stock / Dead Stock / Low Stock / Overstocked / Normal).",
    },
    # --- Stores ---
    {
        "id": "kpi_stores",
        "category": "Stores",
        "content": "Store Performance (analytics.mv_store_performance): Complete store P&L. Includes total_revenue, total_expenses, net_profit, profit_margin_pct, employee_count, revenue_per_employee, performance_tier (Star/Average/Improving/Needs Attention), revenue_rank, profit_rank.",
    },
    {
        "id": "kpi_regional",
        "category": "Stores",
        "content": "Regional Performance (analytics.vw_regional_performance): Aggregated by region. Shows store_count, total_revenue, total_profit, avg_profit_margin, revenue_per_employee, avg_revenue_per_store.",
    },
    # --- Operations ---
    {
        "id": "kpi_delivery",
        "category": "Operations",
        "content": "Delivery Performance (analytics.vw_delivery_performance): Monthly delivery SLA. Shows total_shipments, avg_delivery_days, on_time_pct, delayed_pct, sla_status (Excellent ≥95% / Good ≥85% / Needs Improvement ≥70% / Critical).",
    },
    {
        "id": "kpi_couriers",
        "category": "Operations",
        "content": "Courier Comparison (analytics.vw_courier_comparison): Performance by courier partner. Includes avg_delivery_days, on_time_pct, speed_rank, reliability_rank.",
    },
    {
        "id": "kpi_returns",
        "category": "Operations",
        "content": "Return Analysis (analytics.vw_return_analysis): Returns broken down by category and reason. Shows return_count, total_refunds, return_rate_pct, refund_rate_pct.",
    },
    # --- Marketing ---
    {
        "id": "kpi_campaigns",
        "category": "Marketing",
        "content": "Campaign Performance (analytics.vw_campaign_performance): Campaign ROI tracking with budget, actual_spend, total_clicks, total_conversions, conversion_rate_pct, cost_per_click, attributed_revenue, roi_pct, campaign_status (Excellent/Good/Break Even/Losing Money).",
    },
    {
        "id": "kpi_channels",
        "category": "Marketing",
        "content": "Channel Performance (analytics.vw_channel_performance): Ad spend efficiency by channel (Google, Facebook, Instagram, etc.). Shows total_spend, clicks, conversions, conversion_rate_pct, efficiency_rank.",
    },
    # --- Alerts ---
    {
        "id": "kpi_alerts",
        "category": "Alerts",
        "content": "Active Alerts (analytics.vw_all_active_alerts): Consolidated business alerts. Types: CRITICAL_STOCK (stock <10), HIGH_VALUE_CHURN (Platinum/Gold inactive 60+ days), REVENUE_ANOMALY (revenue <75% of 7-day avg), DELAYED_SHIPMENT (not shipped in 3 days), HIGH_RETURN_RATE (>15%), LOW_STOCK (stock 10-50). Each has severity (HIGH/MEDIUM/LOW), alert_message, and recommended_action.",
    },
]


def load_knowledge_base() -> int:
    """
    Load KPI knowledge into ChromaDB. Idempotent — skips if already loaded.
    Returns number of documents loaded.
    """
    collection = get_collection()

    if collection.count() >= len(KPI_KNOWLEDGE):
        logger.info(f"Knowledge base already loaded ({collection.count()} documents)")
        return collection.count()

    logger.info(f"Loading {len(KPI_KNOWLEDGE)} knowledge documents into ChromaDB...")

    ids = [k["id"] for k in KPI_KNOWLEDGE]
    documents = [k["content"] for k in KPI_KNOWLEDGE]
    metadatas = [{"category": k["category"]} for k in KPI_KNOWLEDGE]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    final_count = collection.count()
    logger.info(f"Knowledge base loaded: {final_count} documents")
    return final_count


def retrieve_context(query: str, n_results: int = 5, category: Optional[str] = None) -> list[str]:
    """
    Retrieve relevant context from ChromaDB for a user query.
    Returns list of relevant knowledge strings.
    """
    collection = get_collection()

    if collection.count() == 0:
        logger.warning("Knowledge base is empty — loading now")
        load_knowledge_base()

    where_filter = {"category": category} if category else None

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        where=where_filter,
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    # Log retrieval quality
    if documents:
        logger.info(
            f"RAG retrieved {len(documents)} docs for '{query[:50]}...' "
            f"(distances: {[round(d, 3) for d in distances]})"
        )

    return documents


def get_knowledge_stats() -> dict:
    """Get statistics about the knowledge base."""
    try:
        collection = get_collection()
        return {
            "total_documents": collection.count(),
            "collection_name": collection.name,
            "status": "ready" if collection.count() > 0 else "empty",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
