# Reflective Tweet Generator — Single-Agent AI with LLM Reflection Loop

> A production-oriented AI system that drafts high-quality X/Twitter posts with a single Writer Agent and iteratively refines them through a structured LLM reflection loop orchestrated with LangGraph.

## Why this project?

Most tweet generators do single-pass generation with no quality control. This project answers a focused engineering question:

**Does reflection-based iterative refinement measurably improve generated tweet quality versus single-pass generation?**

Design principle:

> **One agent generates. One LLM evaluator reflects. LangGraph controls the loop. Guardrails enforce safety. DeepEval measures performance.**

## Key Architecture Constraint

- **Exactly one agent:** `Tweet Writer Agent`
- **Reflection Reviewer is NOT an agent:** stateless LLM evaluation function returning structured scores + actionable feedback
- **Deterministic routing:** `PASS / REVISE / MAX_ATTEMPTS` is decided by threshold comparison, not by the LLM
- **Hard retry cap:** `MAX_ATTEMPTS` prevents infinite loops; full attempt history is preserved

```text
                    User Query
                        |
                        v
               +------------------+
               | Input Guardrails |
               +--------+---------+
                        |
                        v
               +------------------+
               | Tweet Writer     |
               | Agent            |
               | *** ONLY AGENT **|
               +--------+---------+
                        |
                        v
               +------------------+
               | Reflection /     |
               | LLM Review       |
               | NOT AN AGENT     |
               +--------+---------+
                        |
              +---------+---------+
              |                   |
             PASS               REVISE
              |                   |
              v                   v
     +----------------+   +------------------+
     | Output         |   | SAME Tweet       |
     | Guardrails     |   | Writer Agent     |
     +-------+--------+   | + feedback       |
             |            +--------+---------+
             v                     |
            END <------------------+
```

Runtime topology (LangGraph):

```text
START
 → input_guardrails
 → writer
 → reflection
 → conditional_router
    PASS → output_guardrails → END
    REVISE → writer
    MAX_ATTEMPTS → output_guardrails → END
```

## Current Status

Foundation phase is implemented. Workflow, agents, guardrails, API, UI, and evaluations are scaffolded and tracked on the roadmap.

Implemented:

- Typed configuration with `pydantic-settings` (`app/config.py`)
- Structured JSON logging with `structlog` (`app/logging_config.py`)
- Clean package layout for `agents`, `graph`, `reflection`, `guardrails`, `llm`, `prompts`, `models`, `api`
- Test foundation with mocked LLM defaults (`tests/conftest.py`, `tests/test_config.py`)
- Environment template (`.env.example`), lint/type/test tooling (`ruff`, `mypy`, `pytest`)

Planned:

- LangGraph state + nodes + conditional routing
- Input/output guardrails
- Writer agent + reflection reviewer with structured output
- DeepEval offline evaluation + baseline vs. reflection experiment
- FastAPI service + Streamlit UI
- Docker (optional)

See [Roadmap](#roadmap) for the full phase list.

## Project Structure

```text
.
├── app/
│   ├── agents/         # Tweet Writer Agent (the only agent)
│   ├── api/            # FastAPI service (planned)
│   ├── config.py       # Centralized Settings
│   ├── graph/          # LangGraph state, nodes, edges, workflow (planned)
│   ├── guardrails/     # Input / output validation (planned)
│   ├── llm/            # Centralized LLM client (planned)
│   ├── logging_config.py
│   ├── models/         # Shared schemas
│   ├── prompts/        # Writer / reviewer / safety prompts (planned)
│   └── reflection/     # LLM reviewer, NOT an agent (planned)
├── evals/              # DeepEval dataset, metrics, runner (planned)
├── tests/              # pytest suite, LLMs mocked by default
├── ui/                 # Streamlit app (planned)
├── scripts/            # Eval / example runners (planned)
├── reports/            # Generated eval reports (gitignored artifacts)
├── .env.example
├── pyproject.toml
└── AI_Tweet_Generator_Antigravity_Ultimate_Specification.md
```

Full design spec: `AI_Tweet_Generator_Antigravity_Ultimate_Specification.md`

## Quickstart

### Prerequisites

- Python 3.11+
- OpenAI API key

### Install

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -e ".[dev]"

cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

### Configure

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | required | OpenAI API key. Never logged or committed. |
| `WRITER_MODEL` | `gpt-4o-mini` | Model for the Tweet Writer Agent |
| `REVIEWER_MODEL` | `gpt-4o-mini` | Model for the reflection evaluator |
| `SAFETY_MODEL` | `gpt-4o-mini` | Model for input safety classification |
| `WRITER_TEMPERATURE` | `0.7` | Writer creativity |
| `REVIEWER_TEMPERATURE` | `0.3` | Reviewer consistency |
| `MAX_ATTEMPTS` | `3` | Total writer calls: 1 initial + revisions |
| `MAX_TWEET_LENGTH` | `280` | Max tweet length, `len()` characters |
| `REFLECTION_ENABLED` | `true` | `false` = baseline single-pass mode |
| `RELEVANCE_THRESHOLD` | `0.80` | Minimum relevance score for PASS |
| `CLARITY_THRESHOLD` | `0.80` | Minimum clarity score for PASS |
| `PROFESSIONALISM_THRESHOLD` | `0.80` | Minimum professionalism score for PASS |
| `ENGAGEMENT_THRESHOLD` | `0.70` | Minimum engagement score for PASS |
| `REQUIREMENT_THRESHOLD` | `0.85` | Minimum requirement-adherence score for PASS |
| `MAX_INPUT_LENGTH` | `2000` | Max user input length |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

### Run Quality Gates

```bash
pytest
ruff check .
mypy app/
```

Live LLM tests are opt-in and excluded by default:

```bash
pytest -m "not llm"
```

## Reflection Rubric

Each draft is scored `0.0–1.0` on:

- **Relevance** — addresses the request, stays on topic
- **Clarity** — obvious main idea, concise, easy to understand
- **Professionalism** — polished and credible when requested
- **Engagement potential** — strong hook, specificity, natural CTA; not a virality guarantee
- **Requirement adherence** — tone, audience, length, hashtags, CTA, supplied facts

All thresholds must pass for a `PASS`. Otherwise the same Writer Agent receives the original request + previous tweet + feedback + issues + attempt number and revises.

## Evaluation Strategy

- Offline evaluation with DeepEval; runtime reflection stays separate
- Minimum 30-case dataset covering normal, edge, adversarial, and revision-heavy cases
- Baseline (single-pass) vs. reflection compared on the same dataset
- Reports written to `reports/` (`latest.json`, `latest.md`, `comparison.md`) with real measured numbers only — no fabricated results

## API and UI (Planned)

Planned FastAPI surface:

```http
GET /health
POST /generate
```

Example request:

```json
{
  "query": "Write a professional tweet about my AI project",
  "max_attempts": 3,
  "reflection_enabled": true
}
```

Planned Streamlit UI exposes the request, reflection toggle, final tweet, scores, feedback, attempt history, and guardrail status.

## Roadmap

- [x] Phase 0 — Review and Planning
- [x] Phase 1 — Project Foundation
- [ ] Phase 2 — State and Graph Skeleton
- [ ] Phase 3 — Input Guardrails
- [ ] Phase 4 — Tweet Writer Agent
- [ ] Phase 5 — Reflection Reviewer
- [ ] Phase 6 — Reflection Loop
- [ ] Phase 7 — Output Guardrails
- [ ] Phase 8 — Testing Consolidation
- [ ] Phase 9 — DeepEval Evaluation
- [ ] Phase 10 — Baseline vs Reflection
- [ ] Phase 11 — FastAPI
- [ ] Phase 12 — Streamlit UI
- [ ] Phase 13 — Documentation
- [ ] Phase 14 — Optional Docker

## Limitations

- Reflection improves expected quality but cannot guarantee virality or factual correctness without trusted source context.
- LLM-based safety and review steps add latency and cost versus single-pass generation.
- Length enforcement is currently simple character counting.
- API, UI, and DeepEval evaluations are not yet implemented.

## Tech Stack

Python 3.11+ · LangGraph · LangChain · OpenAI · Pydantic · DeepEval · FastAPI · Streamlit · pytest · Ruff · mypy · structlog · python-dotenv

## Security Notes

- `.env` is gitignored; only `.env.example` is committed.
- API keys use `SecretStr` and are never logged.
- Treat all LLM output as untrusted until validated by guardrails.
- Do not expose system prompts, secrets, or stack traces to users.
