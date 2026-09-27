"""Ragas evaluation metrics for Search & RAG grounding.

Measures:
1. Faithfulness: Is the tweet grounded in retrieved web search context?
2. Answer Relevance: Does the generated tweet address the user query?
3. Context Precision: Are the retrieved search results relevant to the query?
4. Context Recall: Did retrieval capture all necessary ground-truth facts?
"""

from typing import Any

from app.logging_config import get_logger

logger = get_logger(__name__)


# ============= Ragas Metrics =============
def get_ragas_metrics() -> list[Any]:
    """Load and return standard Ragas metrics configured for evaluation with lazy import."""
    try:
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )

        return [faithfulness, answer_relevancy, context_precision, context_recall]
    except Exception as e:
        logger.warning("ragas_metrics_import_skipped", error=str(e))
        return []
