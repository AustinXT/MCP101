"""Error handling utilities for GitHub MCP Server."""

from typing import Dict, Any, Optional
import httpx


class MCPError(Exception):
    """Custom exception for MCP server errors."""
    
    def __init__(
        self,
        message: str,
        code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.suggestion = suggestion
        super().__init__(message)


def create_error_response(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response.
    
    Args:
        error_type: Type of error (e.g., 'validation', 'api', 'rate_limit')
        message: Human-readable error message
        details: Additional error details
        
    Returns:
        Standardized error response dictionary
    """
    return {
        "error": {
            "type": error_type,
            "message": message,
            "details": details or {},
            "suggestion": suggest_next_steps(error_type)
        }
    }


def suggest_next_steps(error_type: str) -> str:
    """Provide suggested next steps based on error type.
    
    Args:
        error_type: Type of error encountered
        
    Returns:
        Suggested next steps as a string
    """
    suggestions = {
        "validation": "Check your input parameters and try again.",
        "authentication": (
            "Check your GITHUB_TOKEN environment variable. "
            "Ensure it has the required permissions and is not expired."
        ),
        "rate_limit": (
            "Wait before making more requests. "
            "Consider using a GitHub token with higher rate limits."
        ),
        "not_found": "Verify the repository name and file path are correct.",
        "api_error": "The GitHub API may be experiencing issues. Try again later.",
        "timeout": "The request took too long. Try again with a simpler query.",
        "network": "Check your internet connection and try again."
    }
    
    return suggestions.get(error_type, "Please try again or contact support if the issue persists.")


def handle_api_error(error: httpx.HTTPError) -> MCPError:
    """Handle HTTP errors from GitHub API.
    
    Args:
        error: HTTP error from httpx
        
    Returns:
        Appropriate MCPError
    """
    if isinstance(error, httpx.HTTPStatusError):
        response = error.response
        
        if response.status_code == 401:
            return MCPError(
                message="Authentication failed. Invalid or missing GitHub token.",
                code=401,
                details={"status_code": 401},
                suggestion=suggest_next_steps("authentication")
            )
        elif response.status_code == 403:
            # Check if it's a rate limit error
            rate_limit_remaining = response.headers.get("x-ratelimit-remaining")
            if rate_limit_remaining == "0":
                return MCPError(
                    message="Rate limit exceeded. Please wait before making more requests.",
                    code=429,
                    details={
                        "status_code": 403,
                        "rate_limit_remaining": rate_limit_remaining,
                        "rate_limit_reset": response.headers.get("x-ratelimit-reset")
                    },
                    suggestion=suggest_next_steps("rate_limit")
                )
            else:
                return MCPError(
                    message="Access forbidden. You may not have permission to access this resource.",
                    code=403,
                    details={"status_code": 403},
                    suggestion="Check your token permissions and try again."
                )
        elif response.status_code == 404:
            return MCPError(
                message="Resource not found.",
                code=404,
                details={"status_code": 404},
                suggestion=suggest_next_steps("not_found")
            )
        elif response.status_code == 422:
            return MCPError(
                message="Validation failed. Check your input parameters.",
                code=400,
                details={"status_code": 422},
                suggestion=suggest_next_steps("validation")
            )
        else:
            return MCPError(
                message=f"GitHub API error: {response.status_code}",
                code=response.status_code,
                details={"status_code": response.status_code},
                suggestion=suggest_next_steps("api_error")
            )
    elif isinstance(error, httpx.TimeoutException):
        return MCPError(
            message="Request timeout. The GitHub API took too long to respond.",
            code=408,
            details={"error_type": "timeout"},
            suggestion=suggest_next_steps("timeout")
        )
    elif isinstance(error, httpx.NetworkError):
        return MCPError(
            message="Network error. Unable to connect to GitHub API.",
            code=503,
            details={"error_type": "network"},
            suggestion=suggest_next_steps("network")
        )
    else:
        return MCPError(
            message=f"Unexpected error: {str(error)}",
            code=500,
            details={"error_type": "unknown"},
            suggestion="Please try again or contact support if the issue persists."
        )