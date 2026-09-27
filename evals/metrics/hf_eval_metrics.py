"""Hugging Face Evaluate and deterministic NLP performance metrics."""

import re
from typing import Any

from app.logging_config import get_logger

logger = get_logger(__name__)


# ============ Deterministic Constraint Adherence Metric ============
def compute_constraint_adherence(
    prediction: str,
    must_include: list[str] | None = None,
    forbidden_words: list[str] | None = None,
    required_hashtags: list[str] | None = None,
    max_char_limit: int = 280,
) -> dict[str, Any]:
    """Deterministically check tweet compliance against explicit constraints."""
    text_lower = prediction.lower()

    # Check must_include
    must_include = must_include or []
    missing = [kw for kw in must_include if kw.lower() not in text_lower]
    must_include_passed = len(missing) == 0

    # Check forbidden words
    forbidden_words = forbidden_words or []
    found_forbidden = [fw for fw in forbidden_words if fw.lower() in text_lower]
    forbidden_passed = len(found_forbidden) == 0

    # Check required hashtags
    required_hashtags = required_hashtags or []
    missing_hashtags = [ht for ht in required_hashtags if ht.lower() not in text_lower]
    hashtags_passed = len(missing_hashtags) == 0

    # Length check
    char_count = len(prediction)
    length_passed = char_count <= max_char_limit

    # Overall score: weighted average of checks
    total_checks = 4
    passed_checks = sum([
        1 if must_include_passed else 0,
        1 if forbidden_passed else 0,
        1 if hashtags_passed else 0,
        1 if length_passed else 0,
    ])

    return {
        "score": round(passed_checks / total_checks, 3),
        "char_count": char_count,
        "max_char_limit": max_char_limit,
        "length_passed": length_passed,
        "must_include_passed": must_include_passed,
        "missing_keywords": missing,
        "forbidden_passed": forbidden_passed,
        "found_forbidden": found_forbidden,
        "hashtags_passed": hashtags_passed,
        "missing_hashtags": missing_hashtags,
    }


# =========== ROUGE and BLEU Metrics ===========
def compute_nlp_metrics(
    predictions: list[str],
    references: list[list[str]],
) -> dict[str, Any]:
    """Compute ROUGE and BLEU metrics using Hugging Face evaluate with safe fallbacks."""
    results: dict[str, Any] = {}

    try:
        import evaluate

        # ROUGE
        rouge = evaluate.load("rouge")
        rouge_scores = rouge.compute(predictions=predictions, references=references)
        if rouge_scores:
            results["rouge1"] = round(float(rouge_scores.get("rouge1", 0.0)), 4)
            results["rouge2"] = round(float(rouge_scores.get("rouge2", 0.0)), 4)
            results["rougeL"] = round(float(rouge_scores.get("rougeL", 0.0)), 4)

        # BLEU
        bleu = evaluate.load("bleu")
        bleu_scores = bleu.compute(predictions=predictions, references=references)
        if bleu_scores:
            results["bleu"] = round(float(bleu_scores.get("bleu", 0.0)), 4)

    except Exception as e:
        logger.warning("hf_evaluate_load_failed", error=str(e))
        results["rouge1"] = 0.0
        results["rouge2"] = 0.0
        results["rougeL"] = 0.0
        results["bleu"] = 0.0
        results["note"] = f"HF evaluate fallback: {e}"

    return results


# =========== Lexical Diversity Metric ===========
def compute_lexical_diversity(text: str) -> float:
    """Compute Type-Token Ratio (TTR) as a measure of vocabulary richness."""
    tokens = re.findall(r"\b\w+\b", text.lower())
    if not tokens:
        return 0.0
    return round(len(set(tokens)) / len(tokens), 3)
