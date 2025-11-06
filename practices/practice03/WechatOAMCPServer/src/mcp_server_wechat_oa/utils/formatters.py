"""响应格式化（骨架）"""

import json
from typing import Any, Literal


CHARACTER_LIMIT = 25000 * 4  # ~25k tokens


def format_response(
    data: Any,
    format: Literal["json", "markdown"] = "json",
    detail: Literal["concise", "detailed"] = "concise",
) -> str:
    """
    格式化响应数据。
    """
    if format == "json":
        result = json.dumps(
            extract_concise_data(data) if detail == "concise" else data,
            indent=2,
            ensure_ascii=False,
        )
    else:
        result = (
            format_markdown_concise(data)
            if detail == "concise"
            else format_markdown_detailed(data)
        )

    if len(result) > CHARACTER_LIMIT:
        result = truncate_response(result, CHARACTER_LIMIT)
    return result


def truncate_response(text: str, max_chars: int) -> str:
    """截断过长的响应。"""
    truncated = text[:max_chars]
    return (
        f"""{truncated}

... [Response truncated due to length]

To get complete info:
1. Use more specific filters
2. Request smaller batches
3. Use 'concise' detail level"""
    )


def extract_concise_data(data: Any) -> Any:
    """提取精简数据（TODO）"""
    return data


def format_markdown_concise(data: Any) -> str:
    """格式化为精简 Markdown（TODO）"""
    return "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"


def format_markdown_detailed(data: Any) -> str:
    """格式化为详细 Markdown（TODO）"""
    return format_markdown_concise(data)