"""GitHub MCP Server main file."""

import os
import logging
from fastmcp import FastMCP

# Import tool submodules explicitly to avoid __init__ re-exports
import importlib
search_issues_mod = importlib.import_module("github_mcp_server.tools.search_issues")
list_pull_requests_mod = importlib.import_module("github_mcp_server.tools.list_pull_requests")
get_file_content_mod = importlib.import_module("github_mcp_server.tools.get_file_content")
list_repository_contents_mod = importlib.import_module("github_mcp_server.tools.list_repository_contents")
get_issue_details_mod = importlib.import_module("github_mcp_server.tools.get_issue_details")
get_pull_request_details_mod = importlib.import_module("github_mcp_server.tools.get_pull_request_details")
search_code_mod = importlib.import_module("github_mcp_server.tools.search_code")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("github-mcp-server")


# Create main FastMCP instance
mcp = FastMCP(
    name="GitHub MCP Server",
    version="0.1.0",
    instructions="""
A Model Context Protocol server that provides tools for interacting with GitHub.

Available tools:
- search_issues: Search GitHub issues across repositories
- list_pull_requests: List pull requests for a specific repository
- get_file_content: Get content of files from GitHub repositories
- list_repository_contents: Browse repository file structures

Authentication:
- Set GITHUB_TOKEN environment variable with a GitHub Personal Access Token
- Token requires 'repo' scope for private repositories
- Public repositories can be accessed without authentication (but rate limits apply)

Rate Limits:
- Authenticated requests: 5000 requests per hour
- Unauthenticated requests: 60 requests per hour
- The server handles rate limiting and provides helpful error messages

Response Formats:
- JSON: Structured data for programmatic use
- Markdown: Readable text format for human consumption

Detail Levels:
- Concise: Summary information with key details
- Detailed: Complete information with all available data
"""
)


def check_environment() -> None:
    """Check if required environment variables are set."""
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token or github_token == "your_github_personal_access_token_here":
        logger.warning(
            "GITHUB_TOKEN not set or using default value. "
            "Some features may be limited due to rate restrictions. "
            "Set GITHUB_TOKEN with a valid GitHub Personal Access Token for full functionality."
        )
    else:
        logger.info("GitHub token configured successfully")


def register_tools() -> None:
    """Register tools into the main MCP instance (single FastMCP).

    Note: This function is synchronous so it can be safely called at import time.
    This ensures tools are available when using `fastmcp dev`, which imports the
    module and may not execute the `__main__` block.
    """
    tools_to_register = [
        (search_issues_mod, "search_issues"),
        (list_pull_requests_mod, "list_pull_requests"),
        (get_file_content_mod, "get_file_content"),
        (list_repository_contents_mod, "list_repository_contents"),
        (get_issue_details_mod, "get_issue_details"),
        (get_pull_request_details_mod, "get_pull_request_details"),
        (search_code_mod, "search_code"),
    ]

    for module, func_name in tools_to_register:
        try:
            func = getattr(module, func_name)
            annotations = getattr(module, "TOOL_ANNOTATIONS", {})
            # Register tool function with annotations into the single MCP instance
            mcp.tool(annotations=annotations)(func)
            logger.info(f"Registered tool: {func_name}")
        except Exception as e:
            logger.error(f"Failed to register tool '{func_name}': {e}")


# Register tools at import time so FastMCP dev can discover them immediately
register_tools()


if __name__ == "__main__":
    # Check environment
    check_environment()
    
    # Run the server with stdio transport (default for MCP)
    logger.info("Starting GitHub MCP Server...")
    
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise