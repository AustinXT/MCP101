from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastmcp import Client


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = PROJECT_ROOT / "src" / "mcp_server_wechat_oa" / "server.py"


def setup_sample_markdown(tmpdir: Path) -> None:
    tmpdir.mkdir(parents=True, exist_ok=True)
    sample1 = tmpdir / "a.md"
    sample2 = tmpdir / "b.md"
    sample1.write_text(
        """---
title: 示例文章一
account: 示例公众号
published: 2024-10-01
source_url: https://example.com/a
---

内容一
""",
        encoding="utf-8",
    )
    sample2.write_text(
        """---
title: 示例文章二
account: 示例公众号
published: 2024-10-02
source_url: https://example.com/b
---

内容二
""",
        encoding="utf-8",
    )


def test_end_to_end() -> None:
    # 使用临时目录
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # 1) 测试 summarize_articles
        md_dir = tmp_path / "md"
        setup_sample_markdown(md_dir)

        async def run_summary():
            client = Client(str(SERVER_PATH))
            async with client:
                res = await client.call_tool(
                    "summarize_articles",
                    {
                        "params": {
                            "input_dir": str(md_dir),
                            "pattern": "*.md",
                            "language": "zh",
                        }
                    },
                )
                data = res.data
                assert data["saved"] is True
                assert data["article_count"] == 2
                assert os.path.exists(data["path"]) is True

        import asyncio
        asyncio.run(run_summary())

        # 2) 测试 read_wechat_articles（使用 example.com 作为示例）
        out_dir = tmp_path / "out"

        async def run_read():
            client = Client(str(SERVER_PATH))
            async with client:
                res = await client.call_tool(
                    "read_wechat_articles",
                    {
                        "params": {
                            "urls": ["https://example.com"],
                            "output_dir": str(out_dir),
                            "language": "zh",
                            "account_name": "示例公众号",
                        }
                    },
                )
                data = res.data
                assert data["summary"]["total"] == 1
                assert data["summary"]["succeeded"] == 1
                assert len(data["items"]) == 1
                assert os.path.exists(data["items"][0]["path"]) is True

        asyncio.run(run_read())


if __name__ == "__main__":
    test_end_to_end()