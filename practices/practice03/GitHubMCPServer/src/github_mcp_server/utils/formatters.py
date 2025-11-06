"""Response formatting utilities for GitHub MCP Server."""

import json
from typing import Any, Literal, Dict, List, Optional


# Character limit for responses (~25k tokens)
CHARACTER_LIMIT = 25000 * 4


def format_response(
    data: Any,
    format: Literal["json", "markdown"] = "json",
    detail: Literal["concise", "detailed"] = "concise"
) -> str:
    """Format response data based on requested format and detail level.
    
    Args:
        data: Raw data to format
        format: Output format ("json" or "markdown")
        detail: Detail level ("concise" for summary, "detailed" for full info)
        
    Returns:
        Formatted response string
    """
    if format == "json":
        formatted = format_json(data, detail)
    else:  # markdown
        formatted = format_markdown(data, detail)
    
    # Apply character limit
    return truncate_response(formatted, CHARACTER_LIMIT)


def format_json(data: Any, detail: str) -> str:
    """Format data as JSON.
    
    Args:
        data: Data to format
        detail: Detail level
        
    Returns:
        JSON formatted string
    """
    if detail == "concise":
        concise_data = extract_concise_data(data)
        return json.dumps(concise_data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(data, indent=2, ensure_ascii=False)


def format_markdown(data: Any, detail: str) -> str:
    """Format data as Markdown.
    
    Args:
        data: Data to format
        detail: Detail level
        
    Returns:
        Markdown formatted string
    """
    if detail == "concise":
        return format_markdown_concise(data)
    else:
        return format_markdown_detailed(data)


def format_markdown_concise(data: Any) -> str:
    """Format data as concise Markdown.
    
    Args:
        data: Data to format
        
    Returns:
        Concise Markdown string
    """
    if isinstance(data, dict):
        return format_dict_markdown_concise(data)
    elif isinstance(data, list):
        return format_list_markdown_concise(data)
    else:
        return str(data)


def format_markdown_detailed(data: Any) -> str:
    """Format data as detailed Markdown.
    
    Args:
        data: Data to format
        
    Returns:
        Detailed Markdown string
    """
    if isinstance(data, dict):
        return format_dict_markdown_detailed(data)
    elif isinstance(data, list):
        return format_list_markdown_detailed(data)
    else:
        return f"```\n{str(data)}\n```"


def format_dict_markdown_concise(data: Dict[str, Any]) -> str:
    """Format dictionary as concise Markdown.
    
    Args:
        data: Dictionary to format
        
    Returns:
        Concise Markdown table
    """
    lines = ["| Key | Value |", "|-----|-------|"]
    
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value_str = f"{type(value).__name__} ({len(value) if isinstance(value, list) else 'object'})"
        else:
            value_str = str(value)[:100] + ("..." if len(str(value)) > 100 else "")
        
        lines.append(f"| {key} | {value_str} |")
    
    return "\n".join(lines)


def format_dict_markdown_detailed(data: Dict[str, Any]) -> str:
    """Format dictionary as detailed Markdown.
    
    Args:
        data: Dictionary to format
        
    Returns:
        Detailed Markdown with nested structures
    """
    lines = []
    
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"### {key}")
            lines.append(format_dict_markdown_detailed(value))
        elif isinstance(value, list):
            lines.append(f"### {key} ({len(value)} items)")
            if value and isinstance(value[0], dict):
                lines.append(format_list_markdown_detailed(value))
            else:
                lines.append("\n".join([f"- {item}" for item in value[:10]]))
                if len(value) > 10:
                    lines.append(f"... and {len(value) - 10} more items")
        else:
            lines.append(f"**{key}**: {value}")
    
    return "\n\n".join(lines)


def format_list_markdown_concise(data: List[Any]) -> str:
    """Format list as concise Markdown.
    
    Args:
        data: List to format
        
    Returns:
        Concise Markdown list
    """
    if not data:
        return "No items found"
    
    if isinstance(data[0], dict):
        # For list of objects, show summary
        return f"{len(data)} items found. Use 'detailed' mode for full information."
    else:
        items = data[:5]
        result = "\n".join([f"- {item}" for item in items])
        if len(data) > 5:
            result += f"\n... and {len(data) - 5} more items"
        return result


def format_list_markdown_detailed(data: List[Any]) -> str:
    """Format list as detailed Markdown.
    
    Args:
        data: List to format
        
    Returns:
        Detailed Markdown with tables
    """
    if not data:
        return "No items found"
    
    if isinstance(data[0], dict):
        # Create table from list of objects
        if data:
            keys = list(data[0].keys())
            header = "| " + " | ".join(keys) + " |"
            separator = "|" + "|-".join(["---"] * len(keys)) + "|"
            rows = []
            
            for item in data:
                row = "| " + " | ".join([str(item.get(key, ""))[:50] for key in keys]) + " |"
                rows.append(row)
            
            return f"{header}\n{separator}\n" + "\n".join(rows)
        else:
            return "No items found"
    else:
        return "\n".join([f"- {item}" for item in data])


def extract_concise_data(data: Any) -> Any:
    """Extract concise information from data.
    
    Args:
        data: Raw data to process
        
    Returns:
        Concise version of the data
    """
    if isinstance(data, dict):
        return extract_concise_dict(data)
    elif isinstance(data, list):
        return extract_concise_list(data)
    else:
        return data


def extract_concise_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract concise information from dictionary.
    
    Args:
        data: Dictionary to process
        
    Returns:
        Concise dictionary
    """
    concise_data = {}
    
    for key, value in data.items():
        if key in ["total_count", "items", "name", "full_name", "description", "html_url"]:
            concise_data[key] = value
        elif isinstance(value, dict):
            concise_data[key] = extract_concise_dict(value)
        elif isinstance(value, list):
            concise_data[key] = extract_concise_list(value)
    
    return concise_data


def extract_concise_list(data: List[Any]) -> List[Any]:
    """Extract concise information from list.
    
    Args:
        data: List to process
        
    Returns:
        Concise list (first 5 items)
    """
    if not data:
        return []
    
    if isinstance(data[0], dict):
        return [extract_concise_dict(item) for item in data[:5]]
    else:
        return data[:5]


def truncate_response(text: str, max_chars: int) -> str:
    """Truncate response text if it exceeds character limit.
    
    Args:
        text: Text to truncate
        max_chars: Maximum allowed characters
        
    Returns:
        Truncated text with warning message
    """
    if len(text) <= max_chars:
        return text
    
    truncated = text[:max_chars]
    return f"""{truncated}

... [Response truncated due to length]

To get complete information:
1. Use more specific filters or search terms
2. Request smaller batches with lower 'limit' parameter
3. Use 'concise' detail level instead of 'detailed'
4. Consider using JSON format for better readability of large data
"""