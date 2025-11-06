"""List GitHub pull requests tool (function-only; registration done in server)."""

from pydantic import BaseModel, Field
from typing import Literal
from ..utils.api_client import make_github_request, parse_repository
from ..utils.formatters import format_response
from ..utils.errors import MCPError


class ListPullRequestsInput(BaseModel):
    """Input model for list_pull_requests tool."""
    
    repository: str = Field(
        description="Repository name in format 'owner/repo'. Example: 'facebook/react'",
        min_length=3,
        max_length=100,
        examples=["facebook/react", "microsoft/vscode", "torvalds/linux"]
    )
    
    state: Literal["open", "closed", "all"] = Field(
        default="open",
        description="Filter by pull request state: 'open', 'closed', or 'all'"
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
    
    sort: Literal["created", "updated", "popularity"] = Field(
        default="created",
        description="Sort order: 'created', 'updated', or 'popularity'"
    )
    
    direction: Literal["asc", "desc"] = Field(
        default="desc",
        description="Sort direction: 'asc' for ascending, 'desc' for descending"
    )


# Tool annotations (used by server during registration)
TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": False,
}


async def list_pull_requests(input: ListPullRequestsInput) -> str:
    """List pull requests for a specific GitHub repository.
    
    Use this tool to retrieve pull requests from a specific repository.
    Supports filtering by state, sorting, and pagination.
    
    Args:
        repository: Repository name in format 'owner/repo' (e.g., 'facebook/react')
        state: Filter by pull request state - 'open', 'closed', or 'all'
        format: Output format - "json" for structured data, "markdown" for readable text
        detail: "concise" returns summary information, "detailed" returns full PR details
        limit: Maximum number of results to return (1-100)
        sort: Sort order - "created", "updated", or "popularity"
        direction: Sort direction - "asc" for ascending, "desc" for descending
    
    Returns:
        Formatted list of pull requests for the specified repository
    
    Examples:
        list_pull_requests(repository="facebook/react", state="open", format="json", limit=20)
        list_pull_requests(repository="microsoft/vscode", state="all", format="markdown", detail="detailed")
    
    Error Handling:
        - Invalid repository: Use format 'owner/repo'
        - Repository not found: Check repository name
        - Access denied: Check token permissions
        - Rate limited: Wait before retry
    """
    try:
        # Parse repository name
        repo_info = parse_repository(input.repository)
        
        # Prepare API parameters
        params = {
            "state": input.state,
            "per_page": input.limit,
            "sort": input.sort,
            "direction": input.direction
        }
        
        # Make API request
        response_data = await make_github_request(
            endpoint=f"/repos/{repo_info['owner']}/{repo_info['repo']}/pulls",
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
            message=f"Unexpected error listing pull requests: {str(e)}",
            code=500,
            details={"repository": input.repository},
            suggestion="Please try again or contact support if the issue persists."
        )