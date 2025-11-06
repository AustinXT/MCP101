"""GitHub API client utilities."""

import os
import httpx
import asyncio
from typing import Dict, Any, Optional
from .errors import MCPError, handle_api_error


# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"


async def make_github_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """Make a request to GitHub API.
    
    Args:
        endpoint: API endpoint path (e.g., "/search/issues")
        method: HTTP method (GET, POST, etc.)
        params: Query parameters
        data: Request body data
        timeout: Request timeout in seconds
        
    Returns:
        JSON response from GitHub API
        
    Raises:
        MCPError: If the request fails
    """
    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    
    # Prepare headers
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": "GitHub-MCP-Server/0.1.0"
    }
    if github_token and github_token != "your_github_personal_access_token_here":
        headers["Authorization"] = f"Bearer {github_token}"
    
    # Build full URL
    url = f"{GITHUB_API_BASE}{endpoint}"
    
    # Make the request
    # trust_env=False prevents picking up system HTTP(S)_PROXY/SOCKS settings
    async with httpx.AsyncClient(trust_env=False) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=timeout
            )
            response.raise_for_status()
            
            # Handle rate limiting
            await handle_rate_limit(response)
            
            return response.json()
            
        except httpx.HTTPError as e:
            # Convert HTTP errors to MCP errors
            raise handle_api_error(e)
        except Exception as e:
            raise MCPError(
                message=f"Unexpected error: {str(e)}",
                code=500,
                details={"error_type": "unexpected"},
                suggestion="Please try again or contact support if the issue persists."
            )


async def handle_rate_limit(response: httpx.Response) -> None:
    """Handle GitHub API rate limiting.
    
    Args:
        response: HTTP response from GitHub API
        
    Raises:
        MCPError: If rate limit is exceeded
    """
    rate_limit_remaining = response.headers.get("x-ratelimit-remaining")
    rate_limit_reset = response.headers.get("x-ratelimit-reset")
    
    if rate_limit_remaining and int(rate_limit_remaining) <= 10:
        # If we're getting close to the limit, log a warning
        print(f"Warning: Rate limit getting low. Remaining: {rate_limit_remaining}")
    
    if rate_limit_remaining == "0":
        # Calculate wait time until reset
        reset_time = int(rate_limit_reset) if rate_limit_reset else None
        current_time = asyncio.get_event_loop().time()
        
        if reset_time:
            wait_seconds = max(0, reset_time - current_time)
            raise MCPError(
                message="Rate limit exceeded. Please wait before making more requests.",
                code=429,
                details={
                    "rate_limit_remaining": rate_limit_remaining,
                    "rate_limit_reset": reset_time,
                    "wait_seconds": wait_seconds
                },
                suggestion="Wait before making more requests or use a token with higher limits."
            )


def validate_repository_format(repository: str) -> bool:
    """Validate repository name format (owner/repo).
    
    Args:
        repository: Repository name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not repository or "/" not in repository:
        return False
    
    parts = repository.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False
    
    return True


def parse_repository(repository: str) -> Dict[str, str]:
    """Parse repository name into owner and repo components.
    
    Args:
        repository: Repository name in format "owner/repo"
        
    Returns:
        Dictionary with owner and repo keys
        
    Raises:
        MCPError: If repository format is invalid
    """
    if not validate_repository_format(repository):
        raise MCPError(
            message=f"Invalid repository format: '{repository}'. Expected format: 'owner/repo'.",
            code=400,
            details={"repository": repository},
            suggestion="Use the format 'owner/repo' (e.g., 'facebook/react')."
        )
    
    owner, repo = repository.split("/")
    return {"owner": owner, "repo": repo}