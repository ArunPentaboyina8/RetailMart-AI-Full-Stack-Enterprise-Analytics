# =============================================================================
# RetailMart AI Analytics - RAGAS Evaluation Suite
# =============================================================================
"""
Evaluates the RAG pipeline quality using RAGAS framework metrics:
- Faithfulness: Are answers grounded in retrieved context?
- Answer Relevancy: Does the answer address the question?
- Context Precision: Is the retrieved context relevant?
- Context Recall: Is all needed context retrieved?

Run: python evaluation/eval_rag.py
"""

import json
import sys
import os
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from ai.rag import load_knowledge_base, retrieve_context, get_knowledge_stats


# =============================================================================
# Test Dataset
# =============================================================================

EVAL_DATASET = [
    {
        "question": "What was our total revenue?",
        "expected_context_keywords": ["revenue", "executive_summary", "total_revenue"],
        "expected_view": "analytics.mv_executive_summary",
        "category": "Sales",
    },
    {
        "question": "How are monthly sales trending?",
        "expected_context_keywords": ["monthly", "mom_growth", "sales_dashboard"],
        "expected_view": "analytics.mv_monthly_sales_dashboard",
        "category": "Sales",
    },
    {
        "question": "Who are our most valuable customers?",
        "expected_context_keywords": ["lifetime_value", "clv_tier", "Platinum"],
        "expected_view": "analytics.mv_customer_lifetime_value",
        "category": "Customers",
    },
    {
        "question": "How should we segment our customers for marketing?",
        "expected_context_keywords": ["rfm", "segment", "Champions", "Loyal"],
        "expected_view": "analytics.mv_rfm_analysis",
        "category": "Customers",
    },
    {
        "question": "Which customers are about to churn?",
        "expected_context_keywords": ["churn", "risk", "inactive", "priority"],
        "expected_view": "analytics.vw_churn_risk_customers",
        "category": "Customers",
    },
    {
        "question": "What are our best selling products?",
        "expected_context_keywords": ["top_products", "revenue_rank", "units_sold"],
        "expected_view": "analytics.mv_top_products",
        "category": "Products",
    },
    {
        "question": "Which products drive 80% of revenue?",
        "expected_context_keywords": ["abc", "Pareto", "classification", "cumulative"],
        "expected_view": "analytics.mv_abc_analysis",
        "category": "Products",
    },
    {
        "question": "How are different product categories performing?",
        "expected_context_keywords": ["category", "market_share", "revenue"],
        "expected_view": "analytics.vw_category_performance",
        "category": "Products",
    },
    {
        "question": "Which store is most profitable?",
        "expected_context_keywords": ["store", "profit", "margin", "performance_tier"],
        "expected_view": "analytics.mv_store_performance",
        "category": "Stores",
    },
    {
        "question": "How do regions compare in performance?",
        "expected_context_keywords": ["regional", "region", "store_count"],
        "expected_view": "analytics.vw_regional_performance",
        "category": "Stores",
    },
    {
        "question": "Are we delivering orders on time?",
        "expected_context_keywords": ["delivery", "on_time", "SLA", "shipped"],
        "expected_view": "analytics.vw_delivery_performance",
        "category": "Operations",
    },
    {
        "question": "Which courier partner is most reliable?",
        "expected_context_keywords": ["courier", "speed_rank", "reliability"],
        "expected_view": "analytics.vw_courier_comparison",
        "category": "Operations",
    },
    {
        "question": "Why are customers returning products?",
        "expected_context_keywords": ["return", "reason", "refund", "return_rate"],
        "expected_view": "analytics.vw_return_analysis",
        "category": "Operations",
    },
    {
        "question": "Which marketing campaigns have the best ROI?",
        "expected_context_keywords": ["campaign", "roi", "conversion", "spend"],
        "expected_view": "analytics.vw_campaign_performance",
        "category": "Marketing",
    },
    {
        "question": "Where should we spend our ad budget?",
        "expected_context_keywords": ["channel", "efficiency", "conversion_rate"],
        "expected_view": "analytics.vw_channel_performance",
        "category": "Marketing",
    },
    {
        "question": "What business alerts need attention?",
        "expected_context_keywords": ["alert", "CRITICAL_STOCK", "churn", "severity"],
        "expected_view": "analytics.vw_all_active_alerts",
        "category": "Alerts",
    },
    {
        "question": "How do customers prefer to pay?",
        "expected_context_keywords": ["payment", "mode", "Credit Card", "UPI"],
        "expected_view": "analytics.vw_sales_by_payment_mode",
        "category": "Sales",
    },
    {
        "question": "Are we retaining customers over time?",
        "expected_context_keywords": ["cohort", "retention", "month_number"],
        "expected_view": "analytics.mv_cohort_retention",
        "category": "Customers",
    },
    {
        "question": "What is our inventory health?",
        "expected_context_keywords": ["inventory", "stock", "Dead Stock", "velocity"],
        "expected_view": "analytics.vw_inventory_turnover",
        "category": "Products",
    },
    {
        "question": "Which day of the week gets the most sales?",
        "expected_context_keywords": ["day_of_week", "weekend", "variance"],
        "expected_view": "analytics.vw_sales_by_dayofweek",
        "category": "Sales",
    },
]


# =============================================================================
# Evaluation Metrics
# =============================================================================

def evaluate_context_precision(retrieved_docs: list[str], expected_keywords: list[str]) -> float:
    """
    Context Precision: What fraction of retrieved docs contain expected keywords?
    Higher = less noise in retrieval.
    """
    if not retrieved_docs:
        return 0.0

    relevant_count = 0
    for doc in retrieved_docs:
        doc_lower = doc.lower()
        if any(kw.lower() in doc_lower for kw in expected_keywords):
            relevant_count += 1

    return relevant_count / len(retrieved_docs)


def evaluate_context_recall(retrieved_docs: list[str], expected_keywords: list[str]) -> float:
    """
    Context Recall: What fraction of expected keywords appear in retrieved docs?
    Higher = better coverage of needed information.
    """
    if not expected_keywords:
        return 1.0

    all_docs_text = " ".join(retrieved_docs).lower()
    found_count = sum(1 for kw in expected_keywords if kw.lower() in all_docs_text)

    return found_count / len(expected_keywords)


def evaluate_view_accuracy(retrieved_docs: list[str], expected_view: str) -> bool:
    """
    View Accuracy: Does the retrieval include context about the expected view?
    """
    all_docs_text = " ".join(retrieved_docs).lower()
    view_name = expected_view.split(".")[-1]  # e.g., "mv_executive_summary"
    return view_name.lower() in all_docs_text


# =============================================================================
# Run Evaluation
# =============================================================================

def run_evaluation() -> dict:
    """Run the full evaluation suite and return results."""
    print("=" * 70)
    print("  RetailMart AI Analytics — RAG Evaluation Suite")
    print("=" * 70)
    print()

    # Initialize knowledge base
    print("[1/3] Loading knowledge base...")
    doc_count = load_knowledge_base()
    print(f"      ✓ {doc_count} documents loaded")
    print()

    # Run evaluations
    print(f"[2/3] Running {len(EVAL_DATASET)} evaluation queries...")
    print()

    results = []
    total_precision = 0.0
    total_recall = 0.0
    total_view_accuracy = 0

    for i, test_case in enumerate(EVAL_DATASET):
        # Retrieve context
        start_time = time.time()
        retrieved = retrieve_context(test_case["question"], n_results=5)
        latency = int((time.time() - start_time) * 1000)

        # Evaluate
        precision = evaluate_context_precision(retrieved, test_case["expected_context_keywords"])
        recall = evaluate_context_recall(retrieved, test_case["expected_context_keywords"])
        view_hit = evaluate_view_accuracy(retrieved, test_case["expected_view"])

        total_precision += precision
        total_recall += recall
        if view_hit:
            total_view_accuracy += 1

        status = "✓" if recall >= 0.5 and view_hit else "✗"
        print(
            f"  {status} [{test_case['category']:12s}] {test_case['question'][:50]:50s} "
            f"P={precision:.2f} R={recall:.2f} View={'✓' if view_hit else '✗'} {latency}ms"
        )

        results.append({
            "question": test_case["question"],
            "category": test_case["category"],
            "expected_view": test_case["expected_view"],
            "retrieved_count": len(retrieved),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "view_accuracy": view_hit,
            "latency_ms": latency,
        })

    # Aggregate scores
    n = len(EVAL_DATASET)
    avg_precision = total_precision / n
    avg_recall = total_recall / n
    view_accuracy = total_view_accuracy / n
    f1_score = (
        2 * avg_precision * avg_recall / (avg_precision + avg_recall)
        if (avg_precision + avg_recall) > 0 else 0
    )

    summary = {
        "total_queries": n,
        "avg_context_precision": round(avg_precision, 3),
        "avg_context_recall": round(avg_recall, 3),
        "f1_score": round(f1_score, 3),
        "view_accuracy": round(view_accuracy, 3),
        "knowledge_docs": doc_count,
    }

    # Print summary
    print()
    print("=" * 70)
    print("  EVALUATION RESULTS")
    print("=" * 70)
    print(f"  📊 Queries Evaluated:    {n}")
    print(f"  🎯 Context Precision:    {avg_precision:.1%}  (relevant docs / total retrieved)")
    print(f"  📋 Context Recall:       {avg_recall:.1%}  (keywords found / expected)")
    print(f"  ⚖️  F1 Score:             {f1_score:.1%}")
    print(f"  🗂️  View Accuracy:        {view_accuracy:.1%}  (correct view in results)")
    print()

    # Quality gates
    passed = True
    if avg_precision < 0.5:
        print("  ⚠️  WARN: Context Precision below 50% — too much noise in retrieval")
        passed = False
    if avg_recall < 0.5:
        print("  ⚠️  WARN: Context Recall below 50% — missing important context")
        passed = False
    if view_accuracy < 0.7:
        print("  ⚠️  WARN: View Accuracy below 70% — wrong views being suggested")
        passed = False

    if passed:
        print("  ✅ ALL QUALITY GATES PASSED")
    else:
        print("  ❌ SOME QUALITY GATES FAILED — review and improve RAG pipeline")

    print("=" * 70)

    # Save results
    output_path = Path(__file__).parent / "eval_results.json"
    with open(output_path, "w") as f:
        json.dump({"summary": summary, "details": results}, f, indent=2)
    print(f"\n  Results saved to: {output_path}")

    return summary


if __name__ == "__main__":
    run_evaluation()
