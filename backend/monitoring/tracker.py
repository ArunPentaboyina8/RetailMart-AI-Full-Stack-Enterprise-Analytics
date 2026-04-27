# =============================================================================
# RetailMart AI Analytics - AI Usage Monitoring & Cost Tracking
# =============================================================================
"""
Tracks token usage, latency, costs, and error rates for AI operations.
Implements cost optimization through semantic caching and budget enforcement.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Pricing per 1M tokens (as of 2025, approximate)
MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
}


@dataclass
class UsageRecord:
    """Single AI operation record."""
    question: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    estimated_cost_usd: float
    success: bool
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AIUsageTracker:
    """
    Tracks AI usage metrics for monitoring and cost optimization.
    In-memory tracker — in production, write to database or metrics service.
    """

    _records: list[UsageRecord] = []
    _daily_cost: float = 0.0
    _daily_cost_reset: datetime = datetime.utcnow()

    @classmethod
    def log(
        cls,
        question: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        success: bool,
        error: Optional[str] = None,
    ) -> UsageRecord:
        """Log an AI operation."""
        total = input_tokens + output_tokens
        cost = cls._estimate_cost(model, input_tokens, output_tokens)

        record = UsageRecord(
            question=question[:200],
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total,
            latency_ms=latency_ms,
            estimated_cost_usd=cost,
            success=success,
            error=error,
        )

        cls._records.append(record)

        # Track daily cost
        cls._reset_daily_if_needed()
        cls._daily_cost += cost

        logger.info(
            f"AI Usage: model={model}, tokens={total} "
            f"({input_tokens}in/{output_tokens}out), "
            f"latency={latency_ms}ms, cost=${cost:.6f}, "
            f"daily_total=${cls._daily_cost:.4f}"
        )

        return record

    @classmethod
    def get_stats(cls) -> dict:
        """Get aggregated usage statistics."""
        cls._reset_daily_if_needed()

        if not cls._records:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0,
                "success_rate": 0.0,
                "daily_cost_usd": 0.0,
            }

        total_requests = len(cls._records)
        total_tokens = sum(r.total_tokens for r in cls._records)
        total_cost = sum(r.estimated_cost_usd for r in cls._records)
        avg_latency = sum(r.latency_ms for r in cls._records) / total_requests
        success_count = sum(1 for r in cls._records if r.success)

        # Last 24h stats
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = [r for r in cls._records if r.timestamp > cutoff]

        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "avg_latency_ms": int(avg_latency),
            "success_rate": round(success_count / total_requests * 100, 1),
            "daily_cost_usd": round(cls._daily_cost, 6),
            "requests_24h": len(recent),
            "tokens_24h": sum(r.total_tokens for r in recent),
            "cost_24h": round(sum(r.estimated_cost_usd for r in recent), 6),
            "models_used": list(set(r.model for r in cls._records)),
            "recent_errors": [
                {"question": r.question[:100], "error": r.error, "time": r.timestamp.isoformat()}
                for r in cls._records if not r.success
            ][-5:],
        }

    @classmethod
    def check_budget(cls, max_daily_usd: float) -> tuple[bool, float]:
        """
        Check if daily budget is exceeded.
        Returns (within_budget, remaining_budget).
        """
        cls._reset_daily_if_needed()
        remaining = max_daily_usd - cls._daily_cost
        return remaining > 0, round(remaining, 4)

    @classmethod
    def get_recent_records(cls, limit: int = 20) -> list[dict]:
        """Get recent usage records."""
        records = cls._records[-limit:]
        return [
            {
                "question": r.question[:100],
                "model": r.model,
                "tokens": r.total_tokens,
                "latency_ms": r.latency_ms,
                "cost_usd": r.estimated_cost_usd,
                "success": r.success,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in reversed(records)
        ]

    @staticmethod
    def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on model pricing."""
        # Find the best matching model key
        pricing = None
        for key in MODEL_PRICING:
            if key in model:
                pricing = MODEL_PRICING[key]
                break

        if pricing is None:
            pricing = MODEL_PRICING.get("gpt-4o-mini", {"input": 0.15, "output": 0.60})

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return round(input_cost + output_cost, 8)

    @classmethod
    def _reset_daily_if_needed(cls):
        """Reset daily cost counter if it's a new day."""
        now = datetime.utcnow()
        if now.date() > cls._daily_cost_reset.date():
            cls._daily_cost = 0.0
            cls._daily_cost_reset = now
