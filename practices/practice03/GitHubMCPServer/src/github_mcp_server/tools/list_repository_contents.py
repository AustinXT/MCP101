"""List GitHub repository contents tool (function-only; registration done in server)."""

from pydantic import BaseModel, Field
from typing import Literal, Optional
from ..utils.api_client import make_github_request, parse_repository
from ..utils.formatters import format_response
from ..utils.errors import MCPError


class ListRepositoryContentsInput(BaseModel):
    """Input model for list_repository_contents tool."""
    
    repository: str = Field(
        description="Repository name in format 'owner/repo'. Example: 'facebook/react'",
        min_length=3,
        max_length=100,
        examples=["facebook/react", "microsoft/vscode", "torvalds/linux"]
    )
    
    path: Optional[str] = Field(
        default="",
        description="Directory path within the repository. Empty for root directory",
        max_length=200,
        examples=["src", "docs", "src/components"]
    )
    
    ref: Optional[str] = Field(
        default=None,
        description="Git reference (branch, tag, or commit SHA). Default: repository's default branch",
        examples=["main", "v1.0.0", "a1b2c3d4"]
    )
    
    format: Literal["json", "markdown"] = Field(
        default="json",
        description="Response format: 'json' for structured data, 'markdown' for readable text"
    )
    
    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="Detail level: 'concise' for summary, 'detailed' for full information"
    )
    
    recursive: bool = Field(
        default=False,
        description="Whether to list contents recursively (GitHub API limitation: max 1000 files)"
    )


# Tool annotations (used by server during registration)
TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": False,
}


async def list_repository_contents(input: ListRepositoryContentsInput) -> str:
    """List contents of a GitHub repository directory.
    
    Use this tool to browse repository file structures.
    Shows files and directories with their metadata (size, type, etc.).
    
    Args:
        repository: Repository name in format 'owner/repo' (e.g., 'facebook/react')
        path: Directory path within the repository. Empty for root directory
        ref: Git reference (branch, tag, or commit SHA). Defaults to default branch
        format: Output format - "json" for structured data, "markdown" for readable text
        detail: "concise" returns summary information, "detailed" returns full details
        recursive: Whether to list contents recursively (limited to 1000 files)
    
    Returns:
        Formatted list of repository contents
    
    Examples:
        list_repository_contents(repository="facebook/react", path="src", format="json")
        list_repository_contents(repository="microsoft/vscode", recursive=True, format="markdown")
    
    Error Handling:
        - Invalid repository: Use format 'owner/repo'
        - Directory not found: Check path
        - Access denied: Check token permissions
        - Rate limited: Wait before retry
    """
    try:
        # Parse repository name
        repo_info = parse_repository(input.repository)
        
        # Prepare API parameters
        params = {}
        if input.ref:
            params["ref"] = input.ref
        if input.recursive:
            params["recursive"] = "true"
        
        # Build endpoint URL
        endpoint = f"/repos/{repo_info['owner']}/{repo_info['repo']}/contents"
        if input.path:
            endpoint += f"/{input.path}"
        
        # Make API request
        response_data = await make_github_request(
            endpoint=endpoint,
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
            message=f"Unexpected error listing repository contents: {str(e)}",
            code=500,
            details={
                "repository": input.repository,
                "path": input.path
            },
            suggestion="Please try again or contact support if the issue persists."
        )