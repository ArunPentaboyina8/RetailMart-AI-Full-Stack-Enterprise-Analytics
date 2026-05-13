# =============================================================================
# RetailMart AI Analytics - LangGraph Analytics Agent
# =============================================================================
"""
Multi-step AI agent built with LangGraph for natural language analytics.
Pipeline: Intent → Retrieve Context → Generate SQL → Validate → Execute → Synthesize Answer
"""

import json
import logging
import time
from typing import Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from ai.fallback import FallbackChain
from ai.guardrails import validate_and_sanitize
from ai.prompts import (
    ANSWER_SYNTHESIS_PROMPT,
    FEW_SHOT_EXAMPLES,
    INTENT_CLASSIFICATION_PROMPT,
    SQL_GENERATION_PROMPT,
    SYSTEM_PROMPT,
)
from ai.rag import retrieve_context
from config import get_settings
from database import execute_readonly_query
from monitoring.tracker import AIUsageTracker

logger = logging.getLogger(__name__)

# Response cache (simple in-memory)
_response_cache: dict[str, dict] = {}


# =============================================================================
# Agent State
# =============================================================================

class AgentState(TypedDict):
    """State passed between agent nodes."""
    question: str
    intent: str
    context: list[str]
    sql_query: str
    sql_valid: bool
    sql_error: Optional[str]
    query_results: Optional[list[dict]]
    answer: str
    confidence: float
    sources: list[str]
    model_used: str
    input_tokens: int
    output_tokens: int
    error: Optional[str]
    include_sql: bool
    include_data: bool


# =============================================================================
# Agent Nodes
# =============================================================================

def classify_intent(state: AgentState) -> AgentState:
    """Step 1: Classify the user's question into a business domain."""
    settings = get_settings()

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0,
            max_tokens=20,
        )

        prompt = INTENT_CLASSIFICATION_PROMPT.format(question=state["question"])
        response = llm.invoke([HumanMessage(content=prompt)])

        intent = response.content.strip().upper()

        valid_intents = [
            "SALES", "CUSTOMERS", "PRODUCTS", "STORES",
            "OPERATIONS", "MARKETING", "EXECUTIVE", "OUT_OF_SCOPE"
        ]
        if intent not in valid_intents:
            intent = "EXECUTIVE"

        state["intent"] = intent
        state["input_tokens"] = state.get("input_tokens", 0) + response.usage_metadata.get("input_tokens", 0)
        state["output_tokens"] = state.get("output_tokens", 0) + response.usage_metadata.get("output_tokens", 0)

        logger.info(f"Intent classified: {intent}")

    except Exception as e:
        logger.warning(f"Intent classification failed: {e}, defaulting to EXECUTIVE")
        state["intent"] = "EXECUTIVE"

    return state


def retrieve_knowledge(state: AgentState) -> AgentState:
    """Step 2: Retrieve relevant context from the knowledge base (RAG)."""
    if state["intent"] == "OUT_OF_SCOPE":
        state["context"] = []
        return state

    # Map intent to category filter
    category_map = {
        "SALES": "Sales",
        "CUSTOMERS": "Customers",
        "PRODUCTS": "Products",
        "STORES": "Stores",
        "OPERATIONS": "Operations",
        "MARKETING": "Marketing",
        "EXECUTIVE": None,  # Search all categories
    }

    category = category_map.get(state["intent"])

    try:
        context = retrieve_context(
            query=state["question"],
            n_results=5,
            category=category,
        )
        state["context"] = context
        state["sources"] = [c.split("(")[1].split(")")[0] for c in context if "(" in c and ")" in c]
        logger.info(f"Retrieved {len(context)} context documents")

    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
        state["context"] = []
        state["sources"] = []

    return state


def generate_sql(state: AgentState) -> AgentState:
    """Step 3: Generate SQL query from the question + context."""
    if state["intent"] == "OUT_OF_SCOPE":
        state["sql_query"] = ""
        state["answer"] = (
            "I'm RetailMart Analytics AI — I can help you with questions about "
            "sales, customers, products, stores, operations, and marketing. "
            "Could you ask something related to our retail analytics?"
        )
        state["confidence"] = 0.0
        return state

    settings = get_settings()

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=settings.temperature,
            max_tokens=800,
        )

        # Build context string with few-shot examples
        context_str = "\n\n".join(state["context"]) if state["context"] else "No specific context retrieved."
        examples_str = "\n\n".join([
            f"Q: {ex['question']}\nSQL: {ex['sql']}" for ex in FEW_SHOT_EXAMPLES[:3]
        ])

        prompt = SQL_GENERATION_PROMPT.format(
            context=f"{context_str}\n\n## Similar Examples:\n{examples_str}",
            question=state["question"],
        )

        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        sql = response.content.strip()
        # Clean markdown code blocks if present
        if sql.startswith("```"):
            sql = sql.split("\n", 1)[1] if "\n" in sql else sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        sql = sql.strip()

        state["sql_query"] = sql
        state["model_used"] = settings.gemini_model
        state["input_tokens"] = state.get("input_tokens", 0) + response.usage_metadata.get("input_tokens", 0)
        state["output_tokens"] = state.get("output_tokens", 0) + response.usage_metadata.get("output_tokens", 0)

        logger.info(f"SQL generated: {sql[:100]}...")

    except Exception as e:
        logger.error(f"SQL generation failed: {e}")
        state["sql_query"] = ""
        state["error"] = f"Failed to generate SQL: {str(e)}"

    return state


def validate_sql(state: AgentState) -> AgentState:
    """Step 4: Validate and sanitize the generated SQL."""
    if not state["sql_query"]:
        state["sql_valid"] = False
        return state

    sanitized_sql, error = validate_and_sanitize(state["sql_query"])

    if error:
        state["sql_valid"] = False
        state["sql_error"] = error
        state["sql_query"] = ""
        logger.warning(f"SQL validation failed: {error}")
    else:
        state["sql_valid"] = True
        state["sql_query"] = sanitized_sql
        state["sql_error"] = None
        logger.info("SQL validation passed")

    return state


def execute_sql(state: AgentState) -> AgentState:
    """Step 5: Execute the validated SQL against PostgreSQL."""
    if not state["sql_valid"] or not state["sql_query"]:
        state["query_results"] = None
        return state

    try:
        results = execute_readonly_query(state["sql_query"])
        state["query_results"] = results
        logger.info(f"SQL executed: {len(results)} rows returned")

    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        state["query_results"] = None
        state["error"] = f"Query execution failed: {str(e)}"

    return state


def synthesize_answer(state: AgentState) -> AgentState:
    """Step 6: Generate a natural language answer from the query results."""
    # If we already have an answer (e.g., OUT_OF_SCOPE), skip
    if state.get("answer"):
        return state

    # Handle errors
    if state.get("error"):
        state["answer"] = (
            f"I encountered an issue while analyzing your question: {state['error']}. "
            "Could you try rephrasing your question?"
        )
        state["confidence"] = 0.1
        return state

    if state["query_results"] is None or len(state["query_results"]) == 0:
        state["answer"] = (
            "I wasn't able to find data to answer your question. "
            "This might be because the query returned no results. "
            "Could you try being more specific?"
        )
        state["confidence"] = 0.2
        return state

    settings = get_settings()

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.3,
            max_tokens=settings.max_tokens,
        )

        # Truncate results if too large
        results_str = json.dumps(state["query_results"][:20], indent=2, default=str)
        if len(results_str) > 3000:
            results_str = results_str[:3000] + "\n... (truncated)"

        prompt = ANSWER_SYNTHESIS_PROMPT.format(
            question=state["question"],
            sql_query=state["sql_query"],
            results=results_str,
        )

        response = llm.invoke([
            SystemMessage(content="You are a business analyst providing clear, data-driven insights."),
            HumanMessage(content=prompt),
        ])

        state["answer"] = response.content.strip()
        state["confidence"] = 0.85  # Base confidence for successful execution
        state["input_tokens"] = state.get("input_tokens", 0) + response.usage_metadata.get("input_tokens", 0)
        state["output_tokens"] = state.get("output_tokens", 0) + response.usage_metadata.get("output_tokens", 0)

        logger.info("Answer synthesized successfully")

    except Exception as e:
        logger.error(f"Answer synthesis failed: {e}")
        # Provide raw results as fallback
        state["answer"] = (
            f"Here are the results for your question:\n\n"
            f"```json\n{json.dumps(state['query_results'][:10], indent=2, default=str)}\n```"
        )
        state["confidence"] = 0.5

    return state


# =============================================================================
# Build the LangGraph Agent
# =============================================================================

def build_agent() -> StateGraph:
    """Build the LangGraph analytics agent pipeline."""

    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("retrieve_knowledge", retrieve_knowledge)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("synthesize_answer", synthesize_answer)

    # Define edges (linear pipeline)
    workflow.set_entry_point("classify_intent")
    workflow.add_edge("classify_intent", "retrieve_knowledge")
    workflow.add_edge("retrieve_knowledge", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")
    workflow.add_edge("validate_sql", "execute_sql")
    workflow.add_edge("execute_sql", "synthesize_answer")
    workflow.add_edge("synthesize_answer", END)

    return workflow.compile()


# =============================================================================
# Public API
# =============================================================================

# Global compiled agent
_agent = None


def get_agent():
    """Get or create the compiled agent."""
    global _agent
    if _agent is None:
        _agent = build_agent()
        logger.info("LangGraph analytics agent compiled")
    return _agent


async def ask_analytics(
    question: str,
    include_sql: bool = False,
    include_data: bool = True,
) -> dict:
    """
    Main entry point: ask a natural language question about the data.
    Returns a structured response dict.
    """
    start_time = time.time()
    settings = get_settings()

    # Check cache
    cache_key = question.strip().lower()
    if cache_key in _response_cache:
        cached = _response_cache[cache_key]
        if time.time() - cached["timestamp"] < settings.cache_ttl_seconds:
            logger.info(f"Cache hit for: {question[:50]}")
            cached_response = cached["response"].copy()
            cached_response["cached"] = True
            cached_response["latency_ms"] = int((time.time() - start_time) * 1000)
            return cached_response

    # Initialize state
    initial_state: AgentState = {
        "question": question,
        "intent": "",
        "context": [],
        "sql_query": "",
        "sql_valid": False,
        "sql_error": None,
        "query_results": None,
        "answer": "",
        "confidence": 0.0,
        "sources": [],
        "model_used": settings.gemini_model,
        "input_tokens": 0,
        "output_tokens": 0,
        "error": None,
        "include_sql": include_sql,
        "include_data": include_data,
    }

    try:
        # Run the agent
        agent = get_agent()
        final_state = agent.invoke(initial_state)

        latency_ms = int((time.time() - start_time) * 1000)

        response = {
            "answer": final_state.get("answer", "Unable to generate answer."),
            "sql_query": final_state.get("sql_query") if include_sql else None,
            "data": final_state.get("query_results") if include_data else None,
            "confidence": final_state.get("confidence", 0.0),
            "sources": final_state.get("sources", []),
            "tokens_used": final_state.get("input_tokens", 0) + final_state.get("output_tokens", 0),
            "latency_ms": latency_ms,
            "model_used": final_state.get("model_used", settings.gemini_model),
            "cached": False,
        }

        # Cache the response
        _response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time(),
        }

        # Track usage
        AIUsageTracker.log(
            question=question,
            model=response["model_used"],
            input_tokens=final_state.get("input_tokens", 0),
            output_tokens=final_state.get("output_tokens", 0),
            latency_ms=latency_ms,
            success=True,
        )

        return response

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Agent pipeline failed: {e}")

        # Try fallback
        try:
            fallback_response = FallbackChain.handle(question, str(e))
            return fallback_response
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")

        return {
            "answer": f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}",
            "sql_query": None,
            "data": None,
            "confidence": 0.0,
            "sources": [],
            "tokens_used": 0,
            "latency_ms": latency_ms,
            "model_used": "none",
            "cached": False,
        }
