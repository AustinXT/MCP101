"""Get GitHub file content tool (function-only; registration done in server)."""

from pydantic import BaseModel, Field
from typing import Literal, Optional
import base64
from ..utils.api_client import make_github_request, parse_repository
from ..utils.formatters import format_response
from ..utils.errors import MCPError


class GetFileContentInput(BaseModel):
    """Input model for get_file_content tool."""
    
    repository: str = Field(
        description="Repository name in format 'owner/repo'. Example: 'facebook/react'",
        min_length=3,
        max_length=100,
        examples=["facebook/react", "microsoft/vscode", "torvalds/linux"]
    )
    
    path: str = Field(
        description="File path within the repository. Example: 'src/index.js'",
        min_length=1,
        max_length=200,
        examples=["README.md", "src/index.js", "package.json"]
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


# Tool annotations (used by server during registration)
TOOL_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": False,
}


async def get_file_content(input: GetFileContentInput) -> str:
    """Get content of a file from a GitHub repository.
    
    Use this tool to retrieve file contents from GitHub repositories.
    Supports various file types including code, documentation, and configuration files.
    
    Args:
        repository: Repository name in format 'owner/repo' (e.g., 'facebook/react')
        path: File path within the repository (e.g., 'src/index.js', 'README.md')
        ref: Git reference (branch, tag, or commit SHA). Defaults to default branch
        format: Output format - "json" for structured data, "markdown" for readable text
        detail: "concise" returns summary information, "detailed" returns full file content
    
    Returns:
        Formatted file content with metadata
    
    Examples:
        get_file_content(repository="facebook/react", path="README.md", format="json")
        get_file_content(repository="microsoft/vscode", path="src/main.js", ref="main", format="markdown")
    
    Error Handling:
        - Invalid repository: Use format 'owner/repo'
        - File not found: Check file path
        - Large files: Files over 100MB may not be supported
        - Access denied: Check token permissions
    """
    try:
        # Parse repository name
        repo_info = parse_repository(input.repository)
        
        # Prepare API parameters
        params = {}
        if input.ref:
            params["ref"] = input.ref
        
        # Make API request
        response_data = await make_github_request(
            endpoint=f"/repos/{repo_info['owner']}/{repo_info['repo']}/contents/{input.path}",
            params=params
        )
        
        # Decode base64 content if present
        if "content" in response_data and response_data["content"]:
            try:
                # Remove newlines from base64 content and decode
                content = response_data["content"].replace("\n", "")
                decoded_content = base64.b64decode(content).decode("utf-8")
                response_data["decoded_content"] = decoded_content
                
                # Add language hint based on file extension
                response_data["language"] = detect_language(input.path)
                
            except (base64.binascii.Error, UnicodeDecodeError):
                # Handle binary files or encoding issues
                response_data["decoded_content"] = "[Binary file content not displayed]"
                response_data["is_binary"] = True
        
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
            message=f"Unexpected error getting file content: {str(e)}",
            code=500,
            details={
                "repository": input.repository,
                "path": input.path
            },
            suggestion="Please try again or contact support if the issue persists."
        )


def detect_language(file_path: str) -> str:
    """Detect programming language from file extension.
    
    Args:
        file_path: File path to analyze
        
    Returns:
        Detected language name
    """
    extension_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".html": "HTML",
        ".css": "CSS",
        ".json": "JSON",
        ".yml": "YAML",
        ".yaml": "YAML",
        ".md": "Markdown",
        ".txt": "Text",
        ".xml": "XML",
        ".sql": "SQL",
        ".sh": "Shell",
        ".dockerfile": "Dockerfile",
        ".toml": "TOML",
        ".ini": "INI"
    }
    
    # Get file extension
    if "." in file_path:
        ext = file_path[file_path.rfind("."):].lower()
        return extension_map.get(ext, "Unknown")
    
    return "Unknown"