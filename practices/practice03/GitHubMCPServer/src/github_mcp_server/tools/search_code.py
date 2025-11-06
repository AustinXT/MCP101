"""Search GitHub code tool (function-only; registration done in server)."""

from pydantic import BaseModel, Field
from typing import Literal, Optional
from ..utils.api_client import make_github_request, parse_repository
from ..utils.formatters import format_response
from ..utils.errors import MCPError


class SearchCodeInput(BaseModel):
    """Input model for search_code tool."""

    query: str = Field(
        description="Search query for code. Examples: 'def search', 'filename:README.md', 'extension:py'",
        min_length=1,
        max_length=200,
        examples=["def authenticate", "filename:README.md", "extension:ts"],
    )

    repository: Optional[str] = Field(
        default=None,
        description="Optional repository in format 'owner/repo' to scope the search",
        examples=["facebook/react", "microsoft/vscode"],
    )

    format: Literal["json", "markdown"] = Field(
        default="json",
        description="Response format: 'json' for structured data, 'markdown' for readable text",
    )

    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="Detail level: 'concise' for summary, 'detailed' for full information",
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return (1-100)",
    )


# Tool annotations (used by server during registration)
TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
}


async def search_code(input: SearchCodeInput) -> str:
    """Search code on GitHub, optionally scoped to a repository.

    Args:
        query: Search query for code (supports qualifiers like filename:, extension:, path:)
        repository: Optional repository in format 'owner/repo' to limit the search
        format: Output format - "json" for structured data, "markdown" for readable text
        detail: "concise" returns summary information, "detailed" returns full details
        limit: Maximum number of results to return (1-100)

    Returns:
        Formatted search results for code query

    Examples:
        search_code(query="def login", format="json")
        search_code(query="filename:README.md", repository="facebook/react", format="markdown")
    """
    try:
        # Build query, optionally scoped to repository
        q = input.query
        if input.repository:
            repo_info = parse_repository(input.repository)
            q = f"{q} repo:{repo_info['owner']}/{repo_info['repo']}"

        # Prepare API parameters
        params = {
            "q": q,
            "per_page": input.limit,
        }

        # Make API request
        response_data = await make_github_request(
            endpoint="/search/code",
            params=params,
        )

        # Format response
        formatted_response = format_response(
            response_data,
            format=input.format,
            detail=input.detail,
        )

        return formatted_response

    except MCPError:
        # Re-raise MCP errors
        raise
    except Exception as e:
        # Convert other exceptions to MCP errors
        raise MCPError(
            message=f"Unexpected error searching code: {str(e)}",
            code=500,
            details={"query": input.query, "repository": input.repository},
            suggestion="Please try again or contact support if the issue persists.",
        )