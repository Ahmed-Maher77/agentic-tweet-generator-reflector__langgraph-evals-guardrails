"""FastAPI application for AI Tweet Generator & Reflection Reviewer."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.graph.state import TweetState
from app.graph.workflow import create_tweet_graph
from app.logging_config import get_logger, setup_logging
from app.models.schemas import AttemptRecord, TweetGenerationRequest, TweetGenerationResponse

logger = get_logger(__name__)

# Cached graph instance
_compiled_graph: Any = None

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _compiled_graph
    setup_logging()
    settings = get_settings()
    _compiled_graph = create_tweet_graph(settings=settings)
    logger.info("api_startup_complete", agent="Tweet Writer Agent")
    yield
    logger.info("api_shutdown")


app = FastAPI(
    title="AI Tweet Generator & Reflection Reviewer",
    description="Production-grade AI Tweet Generator with LangGraph-based single-agent reflection loop.",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========== GET ENDPOINT: To check API is live or not ===========
@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "tweet-generator-reviewer",
        "agent": "Tweet Writer Agent (Exactly 1 Agent)",
        "evaluator": "Reflection Reviewer (LLM Evaluation Node)",
    }


# =========== POST ENDPOINT: To Generate and refine a tweet using the LangGraph reflection loop ===========
@app.post(
    "/generate",
    response_model=TweetGenerationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Generation"],
)
async def generate_tweet_endpoint(
    request: TweetGenerationRequest,
) -> TweetGenerationResponse:
    global _compiled_graph
    settings = get_settings()

    graph = _compiled_graph or create_tweet_graph(settings=settings)

    max_att = (
        request.max_attempts
        if request.max_attempts is not None
        else settings.max_attempts
    )
    refl_enabled = (
        request.reflection_enabled
        if request.reflection_enabled is not None
        else settings.reflection_enabled
    )
    srch_enabled = (
        request.search_enabled
        if request.search_enabled is not None
        else settings.search_enabled
    )

    logger.info(
        "api_generation_request_received",
        query_length=len(request.query),
        max_attempts=max_att,
        reflection_enabled=refl_enabled,
        search_enabled=srch_enabled,
    )

    initial_state: TweetState = {
        "user_query": request.query,
        "max_attempts": max_att,
        "reflection_enabled": refl_enabled,
        "search_enabled": srch_enabled,
    }

    try:
        final_state = graph.invoke(initial_state)

        # Convert state attempt history into schema items
        history = [
            AttemptRecord(
                attempt=item["attempt"],
                tweet=item["tweet"],
                review=item.get("review"),
                passed=item.get("passed", False),
            )
            for item in final_state.get("attempt_history", [])
        ]

        logger.info(
            "api_generation_completed",
            status=final_state.get("final_status", "SUCCESS"),
            attempts=final_state.get("attempt", 0),
            search_used=final_state.get("search_used", False),
        )

        return TweetGenerationResponse(
            status=final_state.get("final_status", "SUCCESS"),
            tweet=final_state.get("tweet", ""),
            attempts=final_state.get("attempt", 0),
            reflection_enabled=refl_enabled,
            search_used=final_state.get("search_used", False),
            review=final_state.get("review"),
            attempt_history=history,
            input_blocked=final_state.get("input_blocked", False),
            output_blocked=final_state.get("output_blocked", False),
            block_reason=final_state.get("block_reason"),
        )
    except Exception as exc:
        logger.error("api_generation_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {exc}",
        ) from exc
