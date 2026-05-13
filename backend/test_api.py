"""Quick test of all REST API endpoints against live database."""
import json

import httpx

BASE = "http://localhost:8000"

def test_endpoint(path, label):
    try:
        r = httpx.get(f"{BASE}{path}", timeout=10)
        data = r.json()
        if data.get("success") is False:
            print(f"  X {label}: {data.get('error', 'unknown error')}")
            return
        payload = data.get("data")
        if isinstance(payload, list):
            print(f"  OK {label}: {len(payload)} records")
        elif isinstance(payload, dict):
            print(f"  OK {label}: {json.dumps(payload, default=str)[:120]}...")
        else:
            print(f"  OK {label}: {payload}")
    except Exception as e:
        print(f"  X {label}: {e}")

print("=" * 60)
print("  RetailMart API - Live Data Test")
print("=" * 60)

# Executive
test_endpoint("/api/executive-summary", "Executive Summary")

# Sales
test_endpoint("/api/sales/monthly-trend?limit=3", "Monthly Trend (3)")
test_endpoint("/api/sales/payment-modes", "Payment Modes")
test_endpoint("/api/sales/day-of-week", "Day of Week")

# Customers
test_endpoint("/api/customers/top?limit=5", "Top 5 Customers")
test_endpoint("/api/customers/clv-tiers", "CLV Tiers")
test_endpoint("/api/customers/rfm-segments", "RFM Segments")

# Products
test_endpoint("/api/products/top?limit=5", "Top 5 Products")
test_endpoint("/api/products/categories", "Categories")
test_endpoint("/api/products/abc-analysis", "ABC Analysis")

# Stores
test_endpoint("/api/stores/performance?limit=5", "Store Performance")
test_endpoint("/api/stores/regional", "Regional")

# Operations
test_endpoint("/api/operations/summary", "Ops Summary")
test_endpoint("/api/operations/delivery", "Delivery")
test_endpoint("/api/operations/couriers", "Couriers")

# Marketing
test_endpoint("/api/marketing/campaigns", "Campaigns")
test_endpoint("/api/marketing/channels", "Channels")

# Alerts
r = httpx.get(f"{BASE}/api/alerts", timeout=10)
alerts = r.json()
print(f"  OK Alerts: {alerts['total_count']} total (HIGH={alerts['high_count']}, MED={alerts['medium_count']}, LOW={alerts['low_count']})")

# Health
r = httpx.get(f"{BASE}/health", timeout=10)
h = r.json()
print(f"\n  Health: status={h['status']}, db={h['database']}, vectordb={h['vector_db']}, llm={h['llm_configured']}")

print("=" * 60)
print("  ALL ENDPOINTS TESTED")
print("=" * 60)
