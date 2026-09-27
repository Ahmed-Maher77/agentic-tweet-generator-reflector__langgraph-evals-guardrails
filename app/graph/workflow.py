"""LangGraph workflow assembly and compilation."""

from functools import partial

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.config import Settings, get_settings
from app.graph.edges import (
    route_after_input_guardrails,
    route_after_output_guardrails,
    route_after_reflection,
)
from app.graph.nodes import (
    input_guardrails_node,
    output_guardrails_node,
    reflection_node,
    writer_node,
)
from app.graph.state import TweetState
from app.logging_config import get_logger

logger = get_logger(__name__)


def create_tweet_graph(
    settings: Settings | None = None,
    writer_llm: object | None = None,
    reviewer_model: object | None = None,
) -> CompiledStateGraph:
    """Construct, wire, and compile the Tweet Generation & Reflection StateGraph.

    Topology:
        START
          ↓
        [ input_guardrails ] ──(blocked)──────────────────────────► END
          ↓ (allowed)
        [ writer ] ◄─────────────────────────────────────────────┐
          ↓                                                      │ (revise / retry)
        [ reflection ] ──(revise & attempt < max)────────────────┤
          ↓ (passed OR max attempts reached)                     │
        [ output_guardrails ] ──(failed & retries < max_retries)─┘
          ↓ (passed OR failed & max_retries reached)
        END
    """
    cfg = settings or get_settings()

    builder = StateGraph(TweetState)

    # Bind settings/injected mocks into node functions
    bound_input_guardrails = partial(input_guardrails_node, settings=cfg)
    bound_writer = partial(writer_node, settings=cfg, llm=writer_llm)
    bound_reflection = partial(
        reflection_node,
        settings=cfg,
        structured_model=reviewer_model,
    )
    bound_output_guardrails = partial(output_guardrails_node, settings=cfg)

    # Register Nodes
    builder.add_node("input_guardrails", bound_input_guardrails)
    builder.add_node("writer", bound_writer)
    builder.add_node("reflection", bound_reflection)
    builder.add_node("output_guardrails", bound_output_guardrails)

    # Entry point
    builder.set_entry_point("input_guardrails")

    # Conditional edge from input_guardrails
    builder.add_conditional_edges(
        "input_guardrails",
        route_after_input_guardrails,
        {
            "writer": "writer",
            END: END,
        },
    )

    # Linear edge from writer to reflection
    builder.add_edge("writer", "reflection")

    # Conditional edge from reflection
    builder.add_conditional_edges(
        "reflection",
        route_after_reflection,
        {
            "writer": "writer",
            "output_guardrails": "output_guardrails",
        },
    )

    # Conditional edge from output_guardrails (retry back to writer or exit to END)
    builder.add_conditional_edges(
        "output_guardrails",
        route_after_output_guardrails,
        {
            "writer": "writer",
            END: END,
        },
    )

    logger.info("tweet_graph_compiled_successfully")
    return builder.compile()
