from __future__ import annotations

"""通用 API Client（骨架）

未来迁移到 httpx.AsyncClient 提供异步请求能力。当前保留接口定义与类型提示。
"""

from typing import Any, Dict, Optional


API_BASE_URL = "https://api.example.com"


class MCPError(Exception):
    """统一 MCP 错误类型占位。具体实现放在 utils/errors.py。
    """


async def make_api_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    发起 API 请求的通用异步函数（骨架）。

    Args:
        endpoint: API 端点路径
        method: HTTP 方法
        params: URL 参数
        data: 请求体数据

    Returns:
        API 响应数据（dict）

    Raises:
        MCPError: 当 API 请求失败时
    """
    # TODO: 使用 httpx.AsyncClient 实现并处理错误
    raise NotImplementedError("make_api_request: 待实现 httpx 异步请求")