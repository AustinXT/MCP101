"""Search GitHub issues tool (function-only; registration done in server)."""

from pydantic import BaseModel, Field
from typing import Literal
from ..utils.api_client import make_github_request
from ..utils.formatters import format_response
from ..utils.errors import MCPError


class SearchIssuesInput(BaseModel):
    """Input model for search_issues tool."""
    
    query: str = Field(
        description="Search query for GitHub issues. Examples: 'bug', 'feature request', 'label:bug'",
        min_length=1,
        max_length=200,
        examples=["bug in auth", "feature: dark mode", "label:bug state:open"]
    )
    
    format: Literal["json", "markdown"] = Field(
        default="json",
        description="Response format: 'json' for structured data, 'markdown' for readable text"
    )
    
    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="Detail level: 'concise' for summary, 'detailed' for full information"
    )
    
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return (1-100)"
    )
    
    sort: Literal["created", "updated", "comments"] = Field(
        default="created",
        description="Sort order: 'created', 'updated', or 'comments'"
    )
    
    order: Literal["asc", "desc"] = Field(
        default="desc",
        description="Sort direction: 'asc' for ascending, 'desc' for descending"
    )


# Tool annotations (used by server during registration)
TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
}


async def search_issues(input: SearchIssuesInput) -> str:
    """Search GitHub issues with advanced filtering.
    
    Use this tool to find issues across GitHub repositories based on search criteria.
    Supports searching by keywords, labels, state, repository, and more.
    
    Args:
        query: Search query for issues. Can include:
            - Keywords: 'bug', 'feature request'
            - Labels: 'label:bug', 'label:enhancement'
            - State: 'state:open', 'state:closed'
            - Repository: 'repo:facebook/react'
            - Author: 'author:octocat'
        format: Output format - "json" for structured data, "markdown" for readable text
        detail: "concise" returns summary information, "detailed" returns full issue details
        limit: Maximum number of results to return (1-100)
        sort: Sort order - "created", "updated", or "comments"
        order: Sort direction - "asc" for ascending, "desc" for descending
    
    Returns:
        Formatted list of issues matching the search criteria
    
    Examples:
        search_issues(query="bug in auth", format="json", detail="concise", limit=20)
        search_issues(query="feature request label:enhancement", format="markdown", detail="detailed")
    
    Error Handling:
        - Invalid query: Provide valid search terms
        - Too many results: Narrow query or reduce limit
        - Rate limited: Wait before retry (see error message for duration)
        - Authentication failed: Check GITHUB_TOKEN environment variable
    """
    try:
        # Prepare API parameters
        params = {
            "q": input.query,
            "per_page": input.limit,
            "sort": input.sort,
            "order": input.order
        }
        
        # Make API request
        response_data = await make_github_request(
            endpoint="/search/issues",
            params=params
        )
        
        # Format response
        formatted_response = format_response(
            response_data,
            format=input.format,
            detail=input.detail
        )
        
        return formatted_response
        
    except MCPError:
        # Re-raise MCP errors
        raise
    except Exception as e:
        # Convert other exceptions to MCP errors
        raise MCPError(
            message=f"Unexpected error searching issues: {str(e)}",
            code=500,
            details={"query": input.query},
            suggestion="Please try again or contact support if the issue persists."
        )