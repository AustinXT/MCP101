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

from typing import Any, Dict, List, Optional, Literal, Annotated

from fastmcp import FastMCP
from mcp_server_wechat_oa.tools.tool_read import read_wechat_articles as _read_impl
from mcp_server_wechat_oa.tools.tool_summary import summarize_articles as _summary_impl


mcp = FastMCP(name="WechatOAMCPServer (src)")


@mcp.tool(
    name="read_wechat_articles",
    description=(
        "批量读取微信公众号文章并转换为 Markdown（顶部 front matter 强制），"
        "保存到本地目录，并返回每项处理状态。\n\n"
        "参数说明：\n"
        "- urls: 文章 URL 列表（至少 1 个）\n"
        "- output_dir: 输出目录\n"
        "- account_name: 公众号名称（可选）\n"
        "- language: 语言标识（zh 或 en），默认 zh\n"
        "- concurrency: 并发级别（1-16，预留），默认 4\n"
        "- use_headless: 是否使用无头浏览器（未实现），默认 false\n"
    ),
    tags={"wechat", "markdown", "export"},
    meta={"version": "0.1.0", "examples": {
        "basic": {
            "urls": ["https://mp.weixin.qq.com/s/abc123"],
            "output_dir": "./articles",
            "account_name": "某公众号",
            "language": "zh"
        }
    }},
)
def read_wechat_articles(
    urls: List[str],
    output_dir: str,
    account_name: Optional[str] = None,
    language: Literal["zh", "en"] = "zh",
    concurrency: Annotated[int, "并发级别(1-16)"] = 4,
    use_headless: bool = False,
) -> Dict[str, Any]:
    """读取并保存微信文章。

    兼容旧调用方式：如果传入 params 字段，将自动展开。
    """
    return _read_impl({
        "urls": urls,
        "output_dir": output_dir,
        "account_name": account_name,
        "language": language,
        "concurrency": concurrency,
        "use_headless": use_headless,
    })


@mcp.tool(
    name="summarize_articles",
    description=(
        "从本地 Markdown 集合生成汇总摘要 Markdown 文件，"
        "解析顶部 front matter 并可生成 metadata manifest。\n\n"
        "参数说明：\n"
        "- input_dir: Markdown 输入目录\n"
        "- pattern: 文件匹配模式（默认 *.md）\n"
        "- output_file: 输出文件路径（默认 input_dir/SUMMARY.md）\n"
        "- language: 摘要语言（zh 或 en，默认 zh）\n"
        "- style: 摘要样式（预留，默认 bullet）\n"
    ),
    tags={"summary", "markdown"},
    meta={"version": "0.1.0", "examples": {
        "basic": {
            "input_dir": "./articles",
            "pattern": "*.md",
            "language": "zh"
        }
    }},
)
def summarize_articles(
    input_dir: str,
    pattern: Optional[str] = "*.md",
    output_file: Optional[str] = None,
    language: Literal["zh", "en"] = "zh",
    style: str = "bullet",
) -> Dict[str, Any]:
    """生成文章汇总。

    兼容旧调用方式：如果传入 params 字段，将自动展开。
    """
    return _summary_impl({
        "input_dir": input_dir,
        "pattern": pattern,
        "output_file": output_file,
        "language": language,
        "style": style,
    })


def main() -> None:
    """CLI 入口，使用 STDIO 传输运行。"""
    mcp.run()


if __name__ == "__main__":
    main()