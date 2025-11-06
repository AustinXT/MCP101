"""read_wechat_articles 工具实现

说明：
- 使用 requests + BeautifulSoup 进行页面抓取与解析（同步实现，后续可迁移至 httpx 异步）
- 使用 markdownify 转换 HTML 至 Markdown
- 在生成的 Markdown 顶部写入 YAML front matter（强制）
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import os

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from slugify import slugify
import yaml
from pydantic import BaseModel, Field, ValidationError


class ReadInput(BaseModel):
    urls: List[str] = Field(min_length=1, description="微信公众号文章 URL 列表")
    output_dir: str = Field(description="Markdown 输出目录")
    account_name: Optional[str] = Field(default=None, description="公众号名称（可选）")
    language: str = Field(default="zh", description="语言标识，用于 front matter 与元信息")
    concurrency: int = Field(default=4, ge=1, le=16, description="并发级别（占位）")
    use_headless: bool = Field(default=False, description="是否使用无头浏览器（未实现）")


def _extract_wechat_article(html: str) -> Dict[str, Any]:
    """从微信文章 HTML 提取标题与正文 HTML。"""
    soup = BeautifulSoup(html, "html.parser")

    # 常见结构：h1#activity-name 或 meta og:title
    title = None
    h1 = soup.select_one("h1#activity-name")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)
    if not title:
        meta_title = soup.select_one("meta[property='og:title']")
        if meta_title and meta_title.get("content"):
            title = meta_title.get("content")
    if not title:
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            title = title_tag.get_text(strip=True)

    # 正文容器一般为 #js_content 或 .rich_media_content
    content_container = soup.select_one("#js_content") or soup.select_one(".rich_media_content")
    content_html = str(content_container) if content_container else str(soup.body or soup)

    return {"title": title or "未命名文章", "content_html": content_html}


def _build_front_matter(
    *,
    title: str,
    source_url: str,
    account_name: Optional[str],
    language: str,
    published: Optional[str] = None,
) -> str:
    """构建 YAML front matter 字符串。"""
    fm = {
        "title": title,
        "source_url": source_url,
        "account": account_name or "",
        "published": published or datetime.now().strftime("%Y-%m-%d"),
        "language": language,
    }
    return "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n\n"


def read_wechat_articles(params: Dict[str, Any]) -> Dict[str, Any]:
    """批量读取微信公众号文章并保存为带 front matter 的 Markdown。"""
    try:
        input_data = ReadInput.model_validate(params)
    except ValidationError as e:
        return {"summary": {"total": 0, "succeeded": 0, "failed": 0}, "items": [], "errors": [jsonable_error(e)]}

    urls = input_data.urls
    output_dir = input_data.output_dir
    os.makedirs(output_dir, exist_ok=True)

    items: List[Dict[str, Any]] = []
    succeeded = 0
    failed = 0

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
    }

    for url in urls:
        try:
            resp = session.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
            data = _extract_wechat_article(resp.text)
            title = data["title"]
            content_html = data["content_html"]
            content_md = md(content_html, heading_style="ATX")

            front_matter = _build_front_matter(
                title=title,
                source_url=url,
                account_name=input_data.account_name,
                language=input_data.language,
            )

            filename = slugify(title or url) or slugify(datetime.now().isoformat())
            filepath = os.path.join(output_dir, f"{filename}.md")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(front_matter)
                f.write(content_md)

            items.append({"url": url, "path": filepath, "status": "saved"})
            succeeded += 1
        except Exception as e:  # noqa: BLE001
            items.append({"url": url, "error": str(e), "status": "failed"})
            failed += 1

    return {
        "summary": {"total": len(urls), "succeeded": succeeded, "failed": failed},
        "items": items,
        "errors": [],
    }


def jsonable_error(e: Exception) -> Dict[str, Any]:
    return {"code": "validation_error", "message": str(e)}