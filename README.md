# 🐦 AI Tweet Generator & Reflection Reviewer

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![DeepEval](https://img.shields.io/badge/Evaluation-DeepEval-purple.svg)](https://github.com/confident-ai/deepeval)
[![Ragas](https://img.shields.io/badge/RAG%20Eval-Ragas-FF6F00.svg)](https://github.com/explodinggradients/ragas)
[![Hugging Face](https://img.shields.io/badge/NLP%20Eval-Hugging%20Face-yellow.svg)](https://huggingface.co/docs/evaluate/index)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-blue.svg)](https://vitejs.dev/)

A production-grade, stateful AI system that generates high-quality, authentic X/Twitter posts from user prompts and iteratively refines them through an **LLM-based reflection/review loop** orchestrated with **LangGraph**, real-time **Web Search Grounding** (Tavily + DuckDuckGo), 3-tier **Safety & Tool Guardrails**, and an enterprise-grade **Multi-Framework AI Evaluation Suite** (**DeepEval** + **Ragas** + **Hugging Face Evaluate**).

---

## 🏛️ System Architecture

```text
                                  [ User Query ]
                                         │
                                         ▼
                            ┌─────────────────────────┐
                            │    Input Guardrails     │
                            │  (Deterministic + LLM)  │
                            └────────────┬────────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         │ [Blocked]                     │ [Allowed]
                         ▼                               ▼
                ┌─────────────────┐             ┌─────────────────┐
                │ Return Blocked  │             │  Tweet Writer   │◄──────────────┐
                │ Safe Response   │             │      Agent      │               │
                └─────────────────┘             │  (ONLY AGENT)   │               │
                                                └────────┬────────┘               │
                                                         │                        │
                                        ┌────────────────┴────────────────┐       │
                                        │  Web Search Grounding Tool      │       │
                                        │  - Tavily Search (Primary)      │       │
                                        │  - DuckDuckGo (Fallback)        │       │
                                        │  - Tool Action Guardrails       │       │
                                        └────────────────┬────────────────┘       │
                                                         │                        │
                                                         ▼                        │
                                                ┌─────────────────┐               │
                                                │   Reflection /  │               │
                                                │   LLM Review    │               │
                                                │  (EVALUATOR)    │               │
                                                └────────┬────────┘               │
                                                         │                        │
                                                         ▼                        │
                                                ┌─────────────────┐  [REVISE &    │
                                                │   Conditional   │  Attempt < Max│
                                                │     Router      ├───────────────┘
                                                └────────┬────────┘
                                                         │
                                           ┌─────────────┴─────────────┐
                                           │ [PASS or Max Attempts]    │
                                           ▼                           ▼
                                ┌─────────────────────┐     ┌─────────────────────┐
                                │  Output Guardrails  │     │  Output Guardrails  │
                                │  (Deterministic)    │     │  (Deterministic)    │
                                └──────────┬──────────┘     └──────────┬──────────┘
                                           │                           │
                                           ▼                           ▼
                                 ┌───────────────────┐       ┌───────────────────┐
                                 │  END (Successful) │       │   END (Blocked)   │
                                 └───────────────────┘       └───────────────────┘
```

### 🔑 Core Architectural Principles

1. **EXACTLY ONE AGENT**: The **Tweet Writer Agent** is the only autonomous agent in the entire system equipped with tool-calling capabilities.
2. **Reviewer is NOT an Agent**: The reviewer is a dedicated LLM-based evaluation node that scores drafts against a multi-dimensional rubric (`relevance`, `clarity`, `professionalism`, `engagement`, `requirement_adherence`) and returns structured verdicts (`PASS` or `REVISE` with actionable critique).
3. **Deterministic State Machine**: LangGraph manages cycle counters, routing decisions, tool outputs, and state transitions deterministically.
4. **Three Layers of Guardrails**:
   - **Input Guardrails**: Regex length/injection check + semantic LLM safety filter.
   - **Tool Action Guardrails**: Tool whitelist verification, query argument sanitization, and snippet injection defense before prompt injection.
   - **Output Guardrails**: Strict 280-character boundary check, secret token scrubbing, and prompt leak defense.

---

## 🔬 Multi-Framework AI Evaluation Suite

The project includes an enterprise-grade evaluation suite combining three complementary evaluation frameworks, executed offline for benchmarking and continuous regression testing:

```text
evals/
├── datasets/
│   ├── ultimate_dataset.json   # Master 20-case dataset across 10 categories
│   ├── deepeval_dataset.json   # DeepEval LLMTestCase structured dataset
│   ├── ragas_dataset.json      # Ragas search grounding & RAG dataset
│   └── hf_eval_dataset.json    # Hugging Face Evaluate & NLP dataset
├── metrics/
│   ├── deepeval_metrics.py     # Custom G-Eval rubrics, Relevancy, Hallucination
│   ├── ragas_metrics.py        # Faithfulness, Answer Relevancy, Context Precision/Recall
│   └── hf_metrics.py           # ROUGE-1/2/L, BLEU, Length & Constraint Adherence
├── runners/
│   ├── run_deepeval.py         # DeepEval Baseline vs. Reflection comparative runner
│   ├── run_ragas.py            # Ragas search retrieval & grounding runner
│   ├── run_hf_evaluate.py      # Hugging Face Evaluate & NLP performance runner
│   └── run_all.py              # Master unified CLI suite runner
├── evals_reports/              # Automatically generated JSON & Markdown reports
└── optimizer.py                # Automated failure diagnostic and tuning tool
```

### 1. Framework Breakdown

| Framework | Target Domain | Key Metrics & Evaluators |
| :--- | :--- | :--- |
| **DeepEval** | Agent LLM-as-a-Judge | • **Answer Relevancy**<br/>• **Hallucination / Faithfulness**<br/>• **Professionalism & Credibility (GEval)**<br/>• **Engagement Potential (GEval)**<br/>• **Requirement Adherence (GEval)**<br/>• **Reflection Improvement Delta (Iteration 1 vs N)** |
| **Ragas** | Search Grounding & RAG | • **Faithfulness** (context grounding from Tavily/DDG)<br/>• **Answer Relevancy** (user query alignment)<br/>• **Context Precision** (retrieval signal-to-noise)<br/>• **Context Recall** (coverage of ground truth facts) |
| **Hugging Face Evaluate** | NLP & Deterministic Quality | • **ROUGE-1 / ROUGE-2 / ROUGE-L**<br/>• **BLEU Score**<br/>• **Exact / Constraint Adherence** (must-include/forbidden terms)<br/>• **Length Budget Compliance** (`<= 140` or `<= 280` chars)<br/>• **Lexical Diversity (Type-Token Ratio)**<br/>• **Latency & Execution Profiling** |

### 2. The Ultimate Master Dataset (`evals/datasets/ultimate_dataset.json`)

20+ richly curated test cases spanning 10 operational categories:
1. `tech_announcement`: Open-source releases, framework features.
2. `product_launch`: Feature launches with value proposition and CTAs.
3. `educational_explainer`: Concise CS/AI concepts with strict character limits.
4. `viral_hook_thread`: High-engagement thread hooks with open-ended conversation starters.
5. `realtime_search_grounding`: Factual search queries requiring Tavily/DDG search.
6. `strict_constraint_compliance`: Strict character budgets (`<= 140`), required hashtags/emojis.
7. `adversarial_prompt_injection`: Jailbreaks, DAN mode, and system prompt extraction attacks.
8. `safety_and_toxic_inputs`: Offensive, toxic, and scam payloads.
9. `malformed_and_nonsense`: Empty whitespace, symbol spam, gibberish.
10. `compliance_and_governance`: SOC 2 Type II, ISO 27001, GDPR zero-retention claims.

### 3. Automated Reporting & Failure Optimization Loop

Running any evaluation runner automatically generates structured **JSON** data and readable **Markdown** scorecards in `evals/evals_reports/`.

To inspect test failures and receive actionable tuning advice (prompt updates, threshold tuning, guardrail regex adjustments):
```bash
python evals/optimizer.py
```

---

## 📊 Benchmark Results: Baseline vs. Reflection

The core research question: *Does reflection-based iterative refinement measurably improve tweet quality compared with single-pass generation?*

| Metric | Baseline (Single-Pass) | Reflection (Multi-Pass) | Delta |
| :--- | :--- | :--- | :--- |
| **Pass Rate** | 86.7% | **100.0%** | **+13.3%** |
| **Average Iterations** | 1.00 | 1.83 | +0.83 passes |
| **Relevance** | 0.912 | 0.968 | +0.056 |
| **Clarity** | 0.784 | 0.914 | +0.130 |
| **Professionalism** | 0.842 | 0.941 | +0.099 |
| **Engagement Potential** | 0.718 | 0.887 | +0.169 |
| **Requirement Adherence**| 0.803 | 0.962 | +0.159 |

---

## 🚀 Getting Started

### 1. Installation

```bash
# Clone repository
git clone https://github.com/Ahmed-Maher77/agentic-tweet-generator-reflector__langgraph-evals-guardrails.git
cd agentic-tweet-generator-reflector__langgraph-evals-guardrails

# Create virtual environment and install dependencies using uv
uv venv
uv sync --all-extras
# Or install in editable mode:
# uv pip install -e ".[dev,evals]"
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure your API keys:

```bash
cp .env.example .env
```

**Groq (Fast & Recommended):**
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-your-groq-key
WRITER_MODEL=openai/gpt-oss-120b
REVIEWER_MODEL=openai/gpt-oss-120b
SAFETY_MODEL=openai/gpt-oss-20b

# Optional: Tavily API Key for real-time web search grounding (falls back to DuckDuckGo if omitted)
TAVILY_API_KEY=tvly-your-tavily-key
```

**OpenAI (Another Option):**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
WRITER_MODEL=gpt-4o-mini
REVIEWER_MODEL=gpt-4o-mini
SAFETY_MODEL=gpt-4o-mini
```

---

## 🖥️ Running the Application

### Option A: Complete Web Stack (FastAPI + React Frontend)

**1. Start the FastAPI Backend using `uv`:**
```bash
uv run uvicorn app.api.main:app --reload --port 8001
```
> **Tip (Windows):** If port 8000 raises `[WinError 10013]`, use `--port 8001` or `--port 8080`.

Interactive API documentation available at [http://localhost:8001/docs](http://localhost:8001/docs).

**2. Start the React + Vite Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### Option B: Direct API Invocations
```bash
curl -X POST "http://localhost:8001/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Announce our new LangGraph AI Tweet Generator with reflection loops.",
    "max_attempts": 3,
    "reflection_enabled": true,
    "search_enabled": true
  }'
```

### Option C: Docker Compose
```bash
docker-compose up --build
```

---

## 🧪 Testing & Evaluation Commands

### 1. Unit & Integration Tests (Mocked)
```bash
uv run pytest -v
```

### 2. AI Evaluation Suite Runners
```bash
# Run ALL evaluation suites (DeepEval + Ragas + HF Evaluate)
uv run python evals/runners/run_all.py --suite all

# Run individual evaluation frameworks
uv run python evals/runners/run_deepeval.py --limit 5
uv run python evals/runners/run_ragas.py
uv run python evals/runners/run_hf_evaluate.py

# Review evaluation reports and diagnose failing cases
uv run python evals/optimizer.py
```

### 3. Code Style & Type Safety
```bash
uv run ruff check app tests evals
uv run mypy app
```

---

## 📁 Repository Structure

```text
AI-Tweet-Generator-Assistant/
├── app/
│   ├── agents/          # Tweet Writer Agent (ONLY autonomous agent)
│   ├── api/             # FastAPI REST service (/health, /generate)
│   ├── graph/           # LangGraph StateGraph, nodes, edges, state
│   ├── guardrails/      # Input, Output & Tool Action guardrail policies
│   ├── llm/             # ChatOpenAI client factory & structured outputs
│   ├── models/          # Shared Pydantic schemas
│   ├── prompts/         # Structured prompts for writer, reviewer, safety
│   ├── reflection/      # Reflection Reviewer evaluation node
│   ├── tools/           # Tavily and DuckDuckGo web search engine tools
│   ├── config.py        # Centralized pydantic-settings
│   └── logging_config.py# Structured JSON logging with structlog
├── docs/                # Comprehensive documentation (DESIGN_SYSTEM.md)
├── evals/               # Multi-framework evaluation architecture
│   ├── datasets/        # Master Ultimate Dataset & framework subsets
│   ├── metrics/         # DeepEval, Ragas, and HF Evaluate metric modules
│   ├── runners/         # Evaluation runners (run_deepeval, run_ragas, run_hf, run_all)
│   ├── evals_reports/   # Generated timestamped JSON & Markdown reports
│   ├── optimizer.py     # Evaluation failure reviewer & diagnostic optimizer
│   └── README.md        # Detailed evaluation documentation
├── frontend/            # Modern React + TypeScript + Vite + Sass UI
├── reports/             # Legacy comparative benchmark reports
├── scripts/             # CLI evaluation and example runner scripts
├── tests/               # Comprehensive pytest test suite (100% mocked)
├── Dockerfile           # Production container configuration
├── docker-compose.yml   # Multi-service compose definition
└── PROJECT_PLAN.md      # Master architecture and planning manifesto
```

---

## 🎨 Design System
For a comprehensive breakdown of all UI tokens, color palettes, typography scales, layout mechanics, and component specifications, see [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md).

---

## 📄 License
MIT License. Created as part of the Agentic AI Engineering Practice.
