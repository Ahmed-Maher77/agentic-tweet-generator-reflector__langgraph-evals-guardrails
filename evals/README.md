# Offline Evaluation Suite

This directory contains the modular evaluation architecture for the **AI Tweet Generator Assistant**, organizing datasets, metrics, test runners, and automated reporting across 3 major evaluation frameworks (**DeepEval**, **Ragas**, and **Hugging Face Evaluate**).

---

## 1. Directory Structure

```
evals/
├── datasets/                     # Categorized evaluation datasets, builder, and Golden Set models
│   ├── __init__.py               # Re-exports loaders, test cases, and dataset builder
│   ├── golden_set.py             # GoldenTestCase schema models, loader, and framework converters
│   ├── create_datasets.py        # Programmatic dataset builder & generator for all JSONs
│   ├── llm_generation.json       # Tone, clarity, style, engagement, professionalism
│   ├── rag_search.json           # Real-time search grounding, facts, faithfulness
│   ├── agentic_workflow.json     # Reflection loops, revision iterations, self-correction
│   ├── agent_tool_calling.json   # Writer agent search tool triggering & accuracy
│   ├── general_safety.json       # Toxicity, prompt injection, jailbreaks, malformed inputs
│   └── system_specific.json      # Character budgets (<=280), hashtags, forbidden words
├── metrics/                      # Modular metric suites
│   ├── __init__.py               # Unified exports
│   ├── deepeval_metrics.py       # Answer relevancy, GEval rubrics, hallucination, toxicity, bias
│   ├── ragas_metrics.py          # Faithfulness, answer relevancy, context precision/recall
│   └── hf_eval_metrics.py        # ROUGE-1/2/L, BLEU, deterministic constraint adherence, TTR
├── test_runners/                 # Pytest test classes per evaluation type
│   ├── __init__.py
│   ├── test_llm_generation.py    # Tests LLM quality via DeepEval and GEval
│   ├── test_rag_search.py        # Tests search grounding via Ragas & Hallucination
│   ├── test_agentic_workflow.py  # Tests multi-pass reflection vs. baseline
│   ├── test_agent_tool_calling.py# Tests writer agent tool decisions
│   ├── test_general_safety.py    # Tests guardrail interception & safety
│   └── test_system_specific.py   # Tests constraint adherence (char limit, hashtags)
├── result_reports/               # Generated Markdown & JSON reports
│   └── latest_evaluation_report.md
└── README.md                     # This documentation
```

---

## 2. Evaluation Dimensions & Frameworks

| Domain / Evaluation Type | Target Aspects | Framework & Metrics |
| :--- | :--- | :--- |
| **LLM Generation** | Tone, clarity, developer style, engagement | **DeepEval**: `AnswerRelevancy`, `GEval` (Professionalism, Engagement) |
| **RAG & Search Grounding** | Grounding in search context, zero hallucinations | **Ragas**: `Faithfulness`, `ContextPrecision`, `ContextRecall`<br>**DeepEval**: `HallucinationMetric` |
| **Agentic Workflow** | Self-correction, convergence, loop boundary | **Deterministic**: Max attempts constraint, iteration delta |
| **Agent Tool Calling** | Tool decision accuracy, search trigger logic | **Deterministic & Mocked**: Tool call name & parameters |
| **General Safety** | Prompt injection resistance, toxicity prevention | **Deterministic Guardrails**: `input_blocked == True`<br>**DeepEval**: `ToxicityMetric`, `BiasMetric` |
| **System Constraints** | Character limit (`<= 280`), forbidden buzzwords | **HF Evaluate & Rule-Based**: Constraint compliance score, `ROUGE`, `BLEU`, `TTR` |

---

## 3. How to Run Evaluations

### A. Run via CLI Benchmark Script
To execute the comprehensive benchmark suite across all datasets and produce reports in `evals/result_reports/`:

```bash
# Run complete evaluation suite across all categories
uv run python scripts/run_evals.py

# Run only a specific evaluation domain
uv run python scripts/run_evals.py --eval-type general_safety

# Quick test run with a subset of test cases
uv run python scripts/run_evals.py --sample-limit 2
```

### B. Run via Pytest
To run specific evaluation test runners:

```bash
# Run safety and deterministic constraint runners (fast offline)
uv run pytest evals/test_runners/test_general_safety.py evals/test_runners/test_agent_tool_calling.py -v

# Run live LLM quality runners (requires GROQ_API_KEY or OPENAI_API_KEY)
uv run pytest evals/test_runners/test_llm_generation.py -m llm -v
uv run pytest evals/test_runners/test_rag_search.py -m llm -v
uv run pytest evals/test_runners/test_agentic_workflow.py -m llm -v
```
