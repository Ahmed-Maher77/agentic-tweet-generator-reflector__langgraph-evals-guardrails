"""Golden Set data models and converters for offline multi-framework evaluation."""

import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from app.logging_config import get_logger

logger = get_logger(__name__)

DATASETS_DIR = Path(__file__).parent / "datasets"


# =========== Supported evaluation categories ===========
class EvalType(StrEnum):
    """Supported evaluation categories and dataset identifiers."""

    LLM = "llm_generation"
    RAG = "rag_search"
    AGENTIC_WORKFLOW = "agentic_workflow"
    AGENT_TOOL = "agent_tool_calling"
    GENERAL_SAFETY = "general_safety"
    SYSTEM_SPECIFIC = "system_specific"


# ============ Creating Golden Test Cases ============
@dataclass
class GoldenTestCase:
    """Standardized representation of a single evaluation test case."""

    id: str
    query: str
    category: str
    expected_tone: str | None = None
    must_include: list[str] = field(default_factory=list)
    forbidden_words: list[str] = field(default_factory=list)
    required_hashtags: list[str] = field(default_factory=list)
    max_char_limit: int = 280
    trusted_context: str | None = None
    search_needed: bool = False
    search_query: str | None = None
    ground_truth_reference: str | None = None
    should_use_tool: bool | None = None
    expected_tool: str | None = None
    should_block_input: bool = False
    expected_status: str | None = None
    evaluation_focus: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GoldenTestCase":
        """Instantiate GoldenTestCase from raw dataset dictionary."""
        return cls(
            id=data.get("id", "unknown_id"),
            query=data.get("query", ""),
            category=data.get("category", "general"),
            expected_tone=data.get("expected_tone"),
            must_include=data.get("must_include", []),
            forbidden_words=data.get("forbidden_words", []),
            required_hashtags=data.get("required_hashtags", []),
            max_char_limit=data.get("max_char_limit", 280),
            trusted_context=data.get("trusted_context"),
            search_needed=data.get("search_needed", False),
            search_query=data.get("search_query"),
            ground_truth_reference=data.get("ground_truth_reference"),
            should_use_tool=data.get("should_use_tool"),
            expected_tool=data.get("expected_tool"),
            should_block_input=data.get("should_block_input", False),
            expected_status=data.get("expected_status"),
            evaluation_focus=data.get("evaluation_focus"),
            metadata=data,
        )


def load_dataset(eval_type: EvalType | str) -> list[GoldenTestCase]:
    """Load a specific dataset JSON file and convert into GoldenTestCase objects."""
    name = eval_type.value if isinstance(eval_type, EvalType) else eval_type.replace(".json", "")

    file_path = DATASETS_DIR / f"{name}.json"
    if not file_path.exists():
        logger.error("dataset_file_not_found", path=str(file_path))
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        raw_cases = json.load(f)

    return [GoldenTestCase.from_dict(item) for item in raw_cases]


def load_all_datasets() -> dict[str, list[GoldenTestCase]]:
    """Load all standard evaluation datasets in `evals/datasets/`."""
    datasets: dict[str, list[GoldenTestCase]] = {}
    for eval_enum in EvalType:
        try:
            datasets[eval_enum.value] = load_dataset(eval_enum)
        except FileNotFoundError:
            continue
    return datasets


# ---------------------------------------------------------------------------
# Converters for Evaluation Frameworks (DeepEval, Ragas, HF Evaluate)
# ---------------------------------------------------------------------------

def to_deepeval_test_case(
    test_case: GoldenTestCase,
    actual_output: str,
    retrieval_context: list[str] | None = None,
) -> Any:
    """Convert a GoldenTestCase + LLM output into a DeepEval LLMTestCase."""
    from deepeval.test_case import LLMTestCase

    context = retrieval_context or ([test_case.trusted_context] if test_case.trusted_context else None)
    return LLMTestCase(
        input=test_case.query,
        actual_output=actual_output,
        expected_output=test_case.ground_truth_reference,
        retrieval_context=context,
        context=context,
    )


def to_ragas_dataset(
    test_cases: list[GoldenTestCase],
    predictions: list[str],
    retrieved_contexts: list[list[str]],
) -> Any:
    """Convert test cases and predictions into a Hugging Face / Ragas Dataset."""
    from datasets import Dataset

    records = {
        "question": [tc.query for tc in test_cases],
        "answer": predictions,
        "contexts": retrieved_contexts,
        "ground_truth": [tc.ground_truth_reference or "" for tc in test_cases],
    }
    return Dataset.from_dict(records)


def to_hf_evaluate_inputs(
    test_cases: list[GoldenTestCase],
    predictions: list[str],
) -> tuple[list[str], list[list[str]]]:
    """Convert test cases and predictions into standard format for HF Evaluate (predictions, references)."""
    preds = predictions
    refs = [[tc.ground_truth_reference or ""] for tc in test_cases]
    return preds, refs
