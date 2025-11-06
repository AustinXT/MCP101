"""Get GitHub pull request details tool (function-only; registration done in server)."""

from pydantic import BaseModel, Field
from typing import Literal
from ..utils.api_client import make_github_request, parse_repository
from ..utils.formatters import format_response
from ..utils.errors import MCPError


class GetPullRequestDetailsInput(BaseModel):
    """Input model for get_pull_request_details tool."""

    repository: str = Field(
        description="Repository name in format 'owner/repo'. Example: 'facebook/react'",
        min_length=3,
        max_length=100,
        examples=["facebook/react", "microsoft/vscode", "torvalds/linux"],
    )

    pull_number: int = Field(
        description="Pull request number (e.g., 123)",
        ge=1,
        examples=[1, 42, 1234],
    )

    format: Literal["json", "markdown"] = Field(
        default="json",
        description="Response format: 'json' for structured data, 'markdown' for readable text",
    )

    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="Detail level: 'concise' for summary, 'detailed' for full information",
    )


# Tool annotations (used by server during registration)
TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": False,
}


async def get_pull_request_details(input: GetPullRequestDetailsInput) -> str:
    """Get detailed information for a specific GitHub pull request.

    Args:
        repository: Repository name in format 'owner/repo' (e.g., 'facebook/react')
        pull_number: The pull request number to retrieve
        format: Output format - "json" for structured data, "markdown" for readable text
        detail: "concise" returns summary information, "detailed" returns full PR details

    Returns:
        Formatted pull request details

    Examples:
        get_pull_request_details(repository="facebook/react", pull_number=123, format="json")
        get_pull_request_details(repository="microsoft/vscode", pull_number=42, format="markdown", detail="detailed")
    """
    try:
        # Parse repository name
        repo_info = parse_repository(input.repository)

        # Make API request
        response_data = await make_github_request(
            endpoint=f"/repos/{repo_info['owner']}/{repo_info['repo']}/pulls/{input.pull_number}",
            params={},
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
            message=f"Unexpected error getting pull request details: {str(e)}",
            code=500,
            details={"repository": input.repository, "pull_number": input.pull_number},
            suggestion="Please try again or contact support if the issue persists.",
        )