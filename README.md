# AI Tweet Generator & Reflection Reviewer

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![DeepEval](https://img.shields.io/badge/Evaluation-DeepEval-purple.svg)](https://github.com/confident-ai/deepeval)
[![Ragas](https://img.shields.io/badge/RAG%20Eval-Ragas-FF6F00.svg)](https://github.com/explodinggradients/ragas)
[![Hugging Face](https://img.shields.io/badge/NLP%20Eval-Hugging%20Face-yellow.svg)](https://huggingface.co/docs/evaluate/index)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite%20%2B%20TS-blue.svg)](https://vitejs.dev/)

A production-grade, stateful AI system that generates high-quality, authentic X/Twitter posts from user prompts and iteratively refines them through an **LLM-based reflection/review loop** orchestrated with **LangGraph**, real-time **Web Search Grounding** (Tavily + DuckDuckGo fallback), 3-tier **Safety & Tool Guardrails**, and an enterprise-grade **Multi-Framework AI Evaluation Suite** (**DeepEval** + **Ragas** + **Hugging Face Evaluate**).

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

1. **EXACTLY ONE AGENT**: The **Tweet Writer Agent** is the only autonomous agent in the entire graph equipped with tool-calling capabilities.
2. **Reviewer is NOT an Agent**: The reviewer is a dedicated LLM-based evaluation node that scores drafts against a multi-dimensional rubric (`relevance`, `clarity`, `professionalism`, `engagement`, `requirement_adherence`) and returns structured verdicts (`PASS` or `REVISE` with actionable critique).
3. **Deterministic State Machine**: LangGraph manages cycle counters, routing decisions, tool outputs, and state transitions deterministically.
4. **Three Layers of Guardrails**:
   - **Input Guardrails**: Regex length/injection check + semantic LLM safety filter.
   - **Tool Action Guardrails**: Tool whitelist verification, query argument sanitization, and snippet injection defense before prompt injection.
   - **Output Guardrails**: Strict 280-character boundary check, secret token scrubbing, and prompt leak defense.

---

## 🔬 Multi-Framework AI Evaluation Suite

The project includes an evaluation suite combining three complementary evaluation frameworks, executed offline for benchmarking and continuous regression testing:

```text
evals/
├── datasets/                     # Categorized evaluation datasets & Golden Set models
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
│   ├── latest_evaluation_report.md
│   └── latest_evaluation_report.json
└── README.md                     # Detailed evaluation documentation
```

### 1. Framework Breakdown

| Framework | Target Domain | Key Metrics & Evaluators |
| :--- | :--- | :--- |
| **DeepEval** | Agent LLM-as-a-Judge | • **Answer Relevancy**<br/>• **Hallucination / Faithfulness**<br/>• **Professionalism & Credibility (GEval)**<br/>• **Engagement Potential (GEval)**<br/>• **Requirement Adherence (GEval)**<br/>• **Toxicity & Bias Prevention** |
| **Ragas** | Search Grounding & RAG | • **Faithfulness** (context grounding from Tavily/DDG)<br/>• **Answer Relevancy** (user query alignment)<br/>• **Context Precision** (retrieval signal-to-noise)<br/>• **Context Recall** (coverage of ground truth facts) |
| **Hugging Face Evaluate** | NLP & Deterministic Quality | • **ROUGE-1 / ROUGE-2 / ROUGE-L**<br/>• **BLEU Score**<br/>• **Exact Constraint Adherence** (must-include/forbidden terms)<br/>• **Length Budget Compliance** (`<= 140` or `<= 280` chars)<br/>• **Lexical Diversity (Type-Token Ratio)**<br/>• **Latency & Execution Profiling** |

---

## 📊 Benchmark Results: Baseline vs. Reflection

Empirical evaluation results comparing single-pass baseline generation against the multi-pass reflection loop across 20 real test cases executed on Groq (`openai/gpt-oss-20b`):

| Metric | Baseline (Single-Pass) | Reflection (Multi-Pass) | Delta |
| :--- | :--- | :--- | :--- |
| **Success Rate** | 90.0% | **95.0%** | **+5.0%** |
| **Average Attempts** | 0.80 | 1.00 | +0.20 |
| **Average Latency** | 19.80s | 37.27s | +17.47s |
| **Constraint Adherence** | 0.938 | **0.950** | **+0.012** |
| **Lexical Diversity (TTR)** | 0.917 | 0.916 | -0.001 |
| **Input Blocked (Safety)** | 5 | 5 | 0 |

### 📈 NLP Scores (Hugging Face Evaluate)
- **ROUGE-1**: `0.3253`
- **ROUGE-2**: `0.1350`
- **ROUGE-L**: `0.2697`
- **BLEU**: `0.0657`

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
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure your API keys:

```bash
cp .env.example .env
```

**Option A: Groq Configuration (Ultra-fast inference & high throughput):**
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your-groq-api-key
WRITER_MODEL=openai/gpt-oss-20b
REVIEWER_MODEL=openai/gpt-oss-20b
SAFETY_MODEL=openai/gpt-oss-20b
JUDGE_MODEL=openai/gpt-oss-20b

# Optional: Tavily API Key for real-time web search grounding (falls back to DuckDuckGo if omitted)
TAVILY_API_KEY=tvly-your-tavily-key
```

**Option B: OpenAI Configuration:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
WRITER_MODEL=gpt-4o-mini
REVIEWER_MODEL=gpt-4o-mini
SAFETY_MODEL=gpt-4o-mini
JUDGE_MODEL=gpt-4o-mini

# Optional: Tavily API Key for real-time web search grounding (falls back to DuckDuckGo if omitted)
TAVILY_API_KEY=tvly-your-tavily-key
```

---

## 🖥️ Running the Application

### Option A: Complete Web Stack (FastAPI + React Frontend)

**1. Start the FastAPI Backend using `uv`:**
```bash
uv run uvicorn app.api.main:app --reload --port 8000
```
Interactive API documentation available at [http://localhost:8000/docs](http://localhost:8000/docs).

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
curl -X POST "http://localhost:8000/generate" \
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
uv run pytest tests/ -v
```

### 2. Run Comprehensive Offline Evals via CLI
```bash
# Run full evaluation across all categories (generates Markdown & JSON reports)
uv run python scripts/run_evals.py

# Run specific evaluation category
uv run python scripts/run_evals.py --eval-type general_safety

# Quick sample run
uv run python scripts/run_evals.py --sample-limit 2
```

### 3. Run Specific Pytest Evaluation Runners
```bash
# Safety & tool calling tests (fast offline)
uv run pytest evals/test_runners/test_general_safety.py evals/test_runners/test_agent_tool_calling.py -v

# Live LLM evaluation runners
uv run pytest evals/test_runners/test_llm_generation.py -m llm -v
uv run pytest evals/test_runners/test_rag_search.py -m llm -v
uv run pytest evals/test_runners/test_agentic_workflow.py -m llm -v
```

### 4. Code Quality & Linting
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
│   ├── models/          # Shared Pydantic domain schemas
│   ├── prompts/         # Structured prompts for writer, reviewer, safety
│   ├── reflection/      # Reflection Reviewer evaluation node
│   ├── tools/           # Tavily and DuckDuckGo web search engine tools
│   ├── config.py        # Centralized pydantic-settings
│   └── logging_config.py# Structured JSON logging with structlog
├── docs/                # Comprehensive documentation
│   ├── AI_EVALUATION_FRAMEWORKS_COMPARISON.md
│   ├── DESIGN_SYSTEM.md
│   └── POC_APPROACH_AND_FUTURE_RECOMMENDATIONS.md
├── evals/               # Multi-framework evaluation architecture
│   ├── datasets/        # Categorized test datasets & Golden Set models
│   ├── metrics/         # DeepEval, Ragas, and HF Evaluate metric modules
│   ├── test_runners/    # Pytest evaluation test classes
│   ├── result_reports/  # Generated timestamped JSON & Markdown reports
│   └── README.md        # Detailed evaluation documentation
├── frontend/            # Modern React + TypeScript + Vite + Sass UI
│   ├── src/
│   │   ├── api/         # Backend API client & re-exported types
│   │   ├── components/  # Modular presentational components
│   │   │   ├── common/  # BrandLogo, StatusBadge, Drawer, Modal, HistoryItem, etc.
│   │   │   ├── sidebar/ # SidebarHeader, SidebarNav, SidebarRecentList, SidebarFooter
│   │   │   ├── tweet/   # EngagementButtons
│   │   │   ├── timeline/# TimelineReviewDetails
│   │   │   └── settings/# RubricSlider
│   │   ├── hooks/       # Custom hooks separating logic (usePromptEditor, useTweetCard, etc.)
│   │   ├── scss/        # Apple HIG styling tokens, theme definitions, and layout
│   │   ├── types/       # Centralized TypeScript definitions
│   │   ├── App.tsx      # Main application container
│   │   └── main.tsx     # Application entrypoint
│   └── package.json
├── scripts/             # Evaluation and example runner CLI scripts
│   ├── run_evals.py     # Master offline evaluation benchmark CLI
│   └── run_examples.py  # Quick generation demo script
├── tests/               # Comprehensive pytest test suite (100% mocked)
├── Dockerfile           # Production container configuration
├── docker-compose.yml   # Multi-service compose definition
├── pyproject.toml       # Python package configuration and dependencies
└── PROJECT_PLAN.md      # Architecture and design specifications
```

---

## 🎨 Design System
For a comprehensive breakdown of all UI tokens, color palettes, typography scales, layout mechanics, and component specifications, see [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md).

---

## 📄 License
MIT License. Created as part of the Agentic AI Engineering Practice.
