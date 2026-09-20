"""AI Tweet Generator & Reflection Reviewer.

A production-quality AI system that generates X/Twitter posts and iteratively
improves them through an LLM-based reflection loop.

Architecture:
    - Exactly ONE agent: Tweet Writer Agent
    - Reflection Reviewer: LLM evaluator (NOT an agent)
    - LangGraph: Workflow orchestration
    - Guardrails: Input and output validation
    - DeepEval: Offline evaluation
"""
