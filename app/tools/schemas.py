"""Pydantic schemas for agent tools and search inputs."""

from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    """Schema for web search queries invoked by the Tweet Writer Agent."""

    query: str = Field(
        ...,
        description="The focused search query keyword or question to search the web for.",
        min_length=2,
        max_length=300,
    )


class SearchResult(BaseModel):
    """Normalized search result item."""

    title: str = Field(default="", description="Webpage or article title.")
    url: str = Field(default="", description="Source URL.")
    snippet: str = Field(default="", description="Summarized content snippet.")
