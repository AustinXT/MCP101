"""summarize_articles 工具实现

说明：
- 扫描本地 Markdown 文件，解析 YAML front matter，生成汇总 Markdown
"""

from typing import Any, Dict, List, Optional
import os
import fnmatch
import yaml
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError


class SummaryInput(BaseModel):
    input_dir: str = Field(description="Markdown 输入目录")
    pattern: Optional[str] = Field(default="*.md", description="文件匹配模式（fnmatch）")
    output_file: Optional[str] = Field(default=None, description="汇总输出文件路径，默认写入 input_dir/SUMMARY.md")
    language: str = Field(default="zh", description="摘要语言（zh 或 en）")
    style: str = Field(default="bullet", description="摘要样式（预留）")


def _parse_front_matter(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("---\n"):
        try:
            end = content.find("\n---\n", 4)
            if end != -1:
                fm_text = content[4:end]
                fm = yaml.safe_load(fm_text) or {}
                return fm
        except Exception:  # noqa: BLE001
            return {}
    # 兼容无分隔线但使用 key: value 的情况（简单解析）
    fm: Dict[str, Any] = {}
    for line in content.splitlines()[:20]:
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def summarize_articles(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        input_data = SummaryInput.model_validate(params)
    except ValidationError as e:
        return {"saved": False, "path": "", "article_count": 0, "errors": [jsonable_error(e)]}

    input_dir = input_data.input_dir
    pattern = input_data.pattern or "*.md"
    output_file = input_data.output_file or os.path.join(input_dir, "SUMMARY.md")
    language = input_data.language

    if not os.path.isdir(input_dir):
        return {"saved": False, "path": output_file, "article_count": 0, "errors": [{"code": "not_found", "message": f"目录不存在: {input_dir}"}]}

    articles: List[Dict[str, Any]] = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                path = os.path.join(root, name)
                fm = _parse_front_matter(path)
                articles.append({
                    "title": fm.get("title", os.path.splitext(name)[0]),
                    "account": fm.get("account", ""),
                    "published": fm.get("published", ""),
                    "source_url": fm.get("source_url", ""),
                    "path": path,
                })

    # 语言标签
    LABELS = {
        "zh": {"source": "来源", "account": "账号", "published": "发表于"},
        "en": {"source": "Source", "account": "Account", "published": "Published"},
    }
    labels = LABELS.get(language, LABELS["zh"])

    lines: List[str] = ["# 文章汇总", ""]
    for a in sorted(articles, key=lambda x: (x.get("published") or "", x.get("title") or "")):
        title = a.get("title") or "Untitled"
        source = a.get("source_url") or a.get("path")
        account = a.get("account") or ""
        published = a.get("published") or ""
        lines.append(f"- {title}")
        meta = [
            f"  - {labels['source']}: {source}",
            f"  - {labels['account']}: {account}",
            f"  - {labels['published']}: {published}",
        ]
        lines.extend(meta)
        lines.append("")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:  # noqa: BLE001
        return {"saved": False, "path": output_file, "article_count": len(articles), "errors": [{"code": "write_error", "message": str(e)}]}

    return {"saved": True, "path": output_file, "article_count": len(articles), "errors": []}


def jsonable_error(e: Exception) -> Dict[str, Any]:
    return {"code": "validation_error", "message": str(e)}