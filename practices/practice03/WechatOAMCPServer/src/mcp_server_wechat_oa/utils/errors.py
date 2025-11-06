"""统一错误类型与处理（骨架）"""

from typing import Optional


class MCPError(Exception):
    """MCP 统一错误。"""

    def __init__(self, message: str, *, code: Optional[str] = None) -> None:
        super().__init__(message)
        self.code = code


def handle_api_error(exc: Exception) -> MCPError:
    """将底层异常转换为 MCPError。"""
    return MCPError(str(exc), code="api_error")