"""DeepEval metrics and custom GEval rubrics for tweet generation and reflection."""

import os
from typing import Any

from deepeval.metrics import (
    AnswerRelevancyMetric,
    BiasMetric,
    GEval,
    HallucinationMetric,
    ToxicityMetric,
)
from deepeval.test_case import LLMTestCaseParams



def _get_default_evaluation_model(model: Any = None) -> Any:
    """Return configured evaluation model, defaulting to local OllamaModel."""
    if model is not None:
        return model
    model_name = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").replace("/v1", "").rstrip("/")
    try:
        from deepeval.models import OllamaModel

        return OllamaModel(model=model_name, base_url=base_url)
    except Exception:
        return None


# ======= Answer Relevancy Metric =======
def get_answer_relevancy_metric(
    threshold: float = 0.75,
    model: Any = None,
) -> AnswerRelevancyMetric:
    """DeepEval standard answer relevancy metric assessing semantic query alignment."""
    return AnswerRelevancyMetric(
        threshold=threshold,
        model=_get_default_evaluation_model(model),
        include_reason=True,
    )


# ======= Hallucination / faithfulness Metric =======
def get_hallucination_metric(
    threshold: float = 0.80,
    model: Any = None,
) -> HallucinationMetric:
    """DeepEval hallucination / faithfulness metric assessing fidelity to provided context."""
    return HallucinationMetric(
        threshold=threshold,
        model=_get_default_evaluation_model(model),
        include_reason=True,
    )


# ======= Toxicity Metric =======
def get_toxicity_metric(
    threshold: float = 0.10,
    model: Any = None,
) -> ToxicityMetric:
    """DeepEval toxicity metric assessing hate, harassment, or offensive content."""
    return ToxicityMetric(
        threshold=threshold,
        model=_get_default_evaluation_model(model),
        include_reason=True,
    )


# ======= Bias Metric =======
def get_bias_metric(
    threshold: float = 0.10,
    model: Any = None,
) -> BiasMetric:
    """DeepEval bias metric assessing gender, racial, or demographic bias."""
    return BiasMetric(
        threshold=threshold,
        model=_get_default_evaluation_model(model),
        include_reason=True,
    )


# ======= Professionalism & Credibility Metric =======
def get_professionalism_geval(
    threshold: float = 0.50,
    model: Any = None,
) -> GEval:
    """GEval custom metric evaluating tone, credibility, and appropriateness for social media."""
    return GEval(
        name="Professionalism & Credibility",
        criteria=(
            "Evaluate whether the generated tweet is appropriate for a tech social media audience, "
            "credible, and well-structured. Enthusiastic tone, emojis, and punchy marketing hooks are acceptable on social media."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        evaluation_steps=[
            "Check if the tone is appropriate and respectful for social media audiences.",
            "Verify that the message clearly conveys key technical information without toxic or spammy content.",
            "Score between 0.0 (incoherent or harmful) and 1.0 (clear, credible, and well-crafted).",
        ],
        threshold=threshold,
        model=_get_default_evaluation_model(model),
    )


# ======= Engagement Potential Metric =======
def get_engagement_geval(
    threshold: float = 0.70,
    model: Any = None,
) -> GEval:
    """GEval custom metric evaluating opening hook strength, formatting, and reader interest."""
    return GEval(
        name="Engagement Potential",
        criteria=(
            "Evaluate whether the tweet features a strong opening hook, concise high-value insight, "
            "natural conversational rhythm, and an effective call-to-action or conversation starter."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        evaluation_steps=[
            "Evaluate if the opening line immediately captures reader attention.",
            "Check if the content provides clear, scannable value without fluff.",
            "Score between 0.0 (boring/cluttered) and 1.0 (captivating/high conversational value).",
        ],
        threshold=threshold,
        model=_get_default_evaluation_model(model),
    )


# ======= Requirement Adherence Metric =======
def get_requirement_adherence_geval(
    threshold: float = 0.80,
    model: Any = None,
) -> GEval:
    """GEval custom metric evaluating adherence to explicit prompt constraints."""
    return GEval(
        name="Requirement Adherence",
        criteria=(
            "Evaluate whether the tweet faithfully includes all requested facts, metrics, "
            "topics, hashtags, constraints, and length limits specified in the user request."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        evaluation_steps=[
            "Identify all explicit requirements in the input prompt (numbers, names, hashtags, limits).",
            "Verify that each requirement is present and accurately reflected in the actual output.",
            "Score 1.0 for perfect adherence, reducing score for omitted or altered constraints.",
        ],
        threshold=threshold,
        model=_get_default_evaluation_model(model),
    )


# ======= Reflection Improvement Delta Metric =======
def get_reflection_delta_geval(
    threshold: float = 0.70,
    model: Any = None,
) -> GEval:
    """GEval metric comparing Iteration 1 vs. Final Iteration to verify reflection improvement."""
    return GEval(
        name="Reflection Improvement Delta",
        criteria=(
            "Evaluate whether the revised tweet is measurably better than the initial draft, "
            "specifically addressing reviewer feedback and fixing previously identified issues."
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        evaluation_steps=[
            "Compare the initial draft with the revised final tweet.",
            "Assess whether critique was incorporated and quality improved.",
            "Score between 0.0 (degraded or identical) and 1.0 (significantly improved).",
        ],
        threshold=threshold,
        model=_get_default_evaluation_model(model),
    )
