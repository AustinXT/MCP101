from __future__ import annotations

"""
Wechat OA FastMCP Server (src 结构)

说明：
- 该文件定义一个标准化的 FastMCP 服务器入口，采用 @mcp.tool 注册两类工具：
  1) read_wechat_articles
  2) summarize_articles
- 目前逻辑仍在 practices/practice03/WechatOAMCPServer/server/main.py 中实现。
- 后续将把具体实现迁移到 tools/ 下的模块以实现更清晰的分层。
"""

from typing import Any, Dict

from fastmcp import FastMCP
from mcp_server_wechat_oa.tools.tool_read import read_wechat_articles as _read_impl
from mcp_server_wechat_oa.tools.tool_summary import summarize_articles as _summary_impl


mcp = FastMCP(name="WechatOAMCPServer (src)")


@mcp.tool(
    name="read_wechat_articles",
    description=(
        "批量读取微信公众号文章并转换为 Markdown（顶部 front matter 强制），"
        "保存到本地目录，并返回每项处理状态。"
    ),
    tags={"wechat", "markdown", "export"},
    meta={"version": "0.1.0"},
)
def read_wechat_articles(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    桥接调用现有实现（同步）。
    后续将迁移到 tools/tool_read.py 并改为 Pydantic 输入模型与可选异步实现。
    """
    return _read_impl(params)


@mcp.tool(
    name="summarize_articles",
    description=(
        "从本地 Markdown 集合生成汇总摘要 Markdown 文件，"
        "解析顶部 front matter 并可生成 metadata manifest。"
    ),
    tags={"summary", "markdown"},
    meta={"version": "0.1.0"},
)
def summarize_articles(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    桥接调用现有实现（同步）。
    后续将迁移到 tools/tool_summary.py 并改为 Pydantic 输入模型与可选异步实现。
    """
    return _summary_impl(params)


def main() -> None:
    """CLI 入口，使用 STDIO 传输运行。"""
    mcp.run()


if __name__ == "__main__":
    main()