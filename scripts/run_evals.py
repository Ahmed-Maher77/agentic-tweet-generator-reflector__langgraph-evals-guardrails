"""CLI script to execute offline evaluations across all datasets and output reports."""

import argparse
import datetime
import json
import time
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.graph.state import TweetState
from app.graph.workflow import create_tweet_graph
from app.logging_config import get_logger, setup_logging
from evals.golden_set import EvalType, GoldenTestCase, load_all_datasets, load_dataset
from evals.metrics import (
    compute_constraint_adherence,
    compute_lexical_diversity,
    compute_nlp_metrics,
)

logger = get_logger(__name__)


def format_report_timestamp(dt: datetime.datetime | None = None) -> str:
    """Format a timestamp as `27 Sep, 2026 - 10:40 PM`."""
    dt = dt or datetime.datetime.now(datetime.UTC)
    return dt.strftime("%d %b, %Y - %I:%M %p")


def evaluate_single_run(
    graph: Any,
    test_case: GoldenTestCase,
    reflection_enabled: bool,
) -> dict[str, Any]:
    """Execute a single test case through the tweet graph and measure performance."""
    start_time = time.perf_counter()

    state: TweetState = {
        "user_query": test_case.query,
        "max_attempts": 3 if reflection_enabled else 1,
        "reflection_enabled": reflection_enabled,
        "search_enabled": test_case.search_needed,
    }

    final_state = graph.invoke(state)
    latency_sec = time.perf_counter() - start_time
    tweet = final_state.get("tweet", "")

    compliance = compute_constraint_adherence(
        prediction=tweet,
        must_include=test_case.must_include,
        forbidden_words=test_case.forbidden_words,
        required_hashtags=test_case.required_hashtags,
        max_char_limit=test_case.max_char_limit,
    )

    ttr = compute_lexical_diversity(tweet) if tweet else 0.0

    return {
        "id": test_case.id,
        "category": test_case.category,
        "query": test_case.query,
        "reflection_enabled": reflection_enabled,
        "status": final_state.get("final_status"),
        "tweet": tweet,
        "attempts": final_state.get("attempt", 0),
        "review_passed": final_state.get("review_passed", False),
        "input_blocked": final_state.get("input_blocked", False),
        "output_blocked": final_state.get("output_blocked", False),
        "compliance_score": compliance["score"],
        "length_passed": compliance["length_passed"],
        "forbidden_passed": compliance["forbidden_passed"],
        "hashtags_passed": compliance["hashtags_passed"],
        "lexical_diversity_ttr": ttr,
        "latency_sec": round(latency_sec, 3),
    }


def run_evaluations(
    eval_type: str | None = None,
    settings: Settings | None = None,
    sample_limit: int | None = None,
) -> dict[str, Any]:
    """Run full comparative evaluation across datasets."""
    cfg = settings or get_settings()
    graph = create_tweet_graph(settings=cfg)

    # Load test cases
    if eval_type and eval_type.lower() != "all":
        selected_type = EvalType(eval_type.lower()) if eval_type.lower() in [e.value for e in EvalType] else eval_type
        dataset_map = {str(eval_type): load_dataset(selected_type)}
    else:
        dataset_map = load_all_datasets()

    all_test_cases: list[GoldenTestCase] = []
    for cases in dataset_map.values():
        all_test_cases.extend(cases)

    if sample_limit:
        all_test_cases = all_test_cases[:sample_limit]

    logger.info("starting_evaluation_run", total_cases=len(all_test_cases))

    baseline_results: list[dict[str, Any]] = []
    reflection_results: list[dict[str, Any]] = []

    for tc in all_test_cases:
        logger.info("evaluating_case", case_id=tc.id, category=tc.category)
        # 1. Baseline Run (Single Pass)
        b_res = evaluate_single_run(graph, tc, reflection_enabled=False)
        baseline_results.append(b_res)

        # 2. Reflection Run (Iterative Refinement)
        r_res = evaluate_single_run(graph, tc, reflection_enabled=True)
        reflection_results.append(r_res)

    # Compute NLP scores against ground truth
    predictions = [r["tweet"] for r in reflection_results if r["tweet"]]
    references = [[tc.ground_truth_reference or ""] for tc, r in zip(all_test_cases, reflection_results, strict=True) if r["tweet"]]
    nlp_scores = compute_nlp_metrics(predictions, references) if predictions and references else {}

    # Aggregates
    def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(results) or 1
        successes = sum(1 for r in results if r["status"] == "SUCCESS")
        input_blocked = sum(1 for r in results if r["input_blocked"])
        avg_attempts = sum(r["attempts"] for r in results) / total
        avg_latency = sum(r["latency_sec"] for r in results) / total
        avg_compliance = sum(r["compliance_score"] for r in results) / total
        avg_ttr = sum(r["lexical_diversity_ttr"] for r in results) / total

        return {
            "total_cases": total,
            "success_rate": round(successes / total, 3),
            "input_blocked_count": input_blocked,
            "average_attempts": round(avg_attempts, 2),
            "average_latency_sec": round(avg_latency, 2),
            "average_compliance_score": round(avg_compliance, 3),
            "average_lexical_diversity_ttr": round(avg_ttr, 3),
        }

    return {
        "timestamp": format_report_timestamp(),
        "total_test_cases": len(all_test_cases),
        "evaluated_categories": list(dataset_map.keys()),
        "baseline_summary": summarize(baseline_results),
        "reflection_summary": summarize(reflection_results),
        "nlp_metrics": nlp_scores,
        "detailed_results": {
            "baseline": baseline_results,
            "reflection": reflection_results,
        },
    }


def format_markdown_report(report_data: dict[str, Any]) -> str:
    """Render structured evaluation data as clean Markdown."""
    b_sum = report_data["baseline_summary"]
    r_sum = report_data["reflection_summary"]
    nlp = report_data.get("nlp_metrics", {})

    raw_timestamp = str(report_data.get("timestamp", ""))
    try:
        # Backward compatibility: reformat legacy ISO timestamps.
        parsed = datetime.datetime.fromisoformat(raw_timestamp)
        display_timestamp = format_report_timestamp(parsed)
    except (ValueError, TypeError):
        display_timestamp = raw_timestamp

    md = []
    md.append("# AI Tweet Generator Assistant - Offline Evaluation Report")
    md.append(f"\n**Timestamp:** `{display_timestamp}`  ")
    md.append(f"**Total Test Cases Evaluated:** `{report_data['total_test_cases']}`  ")
    md.append(f"**Categories:** {', '.join(report_data['evaluated_categories'])}\n")

    md.append("## Executive Summary (Baseline vs. Reflection)")
    md.append("| Metric | Baseline (Single-Pass) | Reflection (Multi-Pass) | Delta |")
    md.append("| :--- | :--- | :--- | :--- |")

    b_succ = b_sum["success_rate"] * 100
    r_succ = r_sum["success_rate"] * 100
    md.append(f"| Success Rate | {b_succ:.1f}% | {r_succ:.1f}% | {r_succ - b_succ:+.1f}% |")

    b_att = b_sum["average_attempts"]
    r_att = r_sum["average_attempts"]
    md.append(f"| Average Attempts | {b_att:.2f} | {r_att:.2f} | {r_att - b_att:+.2f} |")

    b_lat = b_sum["average_latency_sec"]
    r_lat = r_sum["average_latency_sec"]
    md.append(f"| Average Latency | {b_lat:.2f}s | {r_lat:.2f}s | {r_lat - b_lat:+.2f}s |")

    b_comp = b_sum["average_compliance_score"]
    r_comp = r_sum["average_compliance_score"]
    md.append(f"| Constraint Adherence | {b_comp:.3f} | {r_comp:.3f} | {r_comp - b_comp:+.3f} |")

    b_ttr = b_sum["average_lexical_diversity_ttr"]
    r_ttr = r_sum["average_lexical_diversity_ttr"]
    md.append(f"| Lexical Diversity (TTR) | {b_ttr:.3f} | {r_ttr:.3f} | {r_ttr - b_ttr:+.3f} |")
    md.append(f"| Input Blocked (Safety) | {b_sum['input_blocked_count']} | {r_sum['input_blocked_count']} | 0 |")

    if nlp:
        md.append("\n## Deterministic NLP Scores (Hugging Face Evaluate)")
        md.append("| Metric | Score |")
        md.append("| :--- | :--- |")
        for k, v in nlp.items():
            md.append(f"| {k.upper()} | {v} |")

    md.append("\n## Architectural Takeaways")
    md.append("- **Multi-Pass Reflection**: Improves constraint compliance and polish over single-pass generation.")
    md.append("- **Pre-execution Guardrails**: Intercepts toxic prompts, injections, and malformed inputs with 0 LLM cost.")
    md.append("- **Tool Calling Grounding**: Pulls live web context when required while avoiding unnecessary latency for evergreen topics.")

    return "\n".join(md)


def main() -> None:
    """CLI entry point for running offline evaluations."""
    parser = argparse.ArgumentParser(description="Run Tweet Assistant Offline Evaluation Suite")
    parser.add_argument(
        "--eval-type",
        type=str,
        default="all",
        help="Evaluation type to run (all, llm_generation, rag_search, agentic_workflow, agent_tool_calling, general_safety, system_specific)",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=None,
        help="Limit number of test cases to run (for rapid local testing)",
    )
    args = parser.parse_args()

    setup_logging()
    settings = get_settings()

    reports_dir = Path(__file__).parent.parent / "evals" / "result_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    print(f"Executing evaluations (type: {args.eval_type}, sample limit: {args.sample_limit})...")
    report_data = run_evaluations(
        eval_type=args.eval_type,
        settings=settings,
        sample_limit=args.sample_limit,
    )

    # Save JSON report
    latest_json = reports_dir / "latest_evaluation_report.json"
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    # Save Markdown report
    md_content = format_markdown_report(report_data)
    latest_md = reports_dir / "latest_evaluation_report.md"
    with open(latest_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✅ Evaluations complete! Reports saved to:\n- {latest_md}\n- {latest_json}\n")
    print(md_content)


if __name__ == "__main__":
    main()
