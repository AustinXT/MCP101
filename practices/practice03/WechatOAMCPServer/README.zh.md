# WechatOAMCPServer（FastMCP 版）

本项目实现了一个基于 Python FastMCP 的 MCP Server，提供两款工具：
- read_wechat_articles：批量读取微信公众号文章 URL，解析为 Markdown，并写入到本地目录。所有 Markdown 文件顶部强制包含 YAML front matter（键值对元信息块）。
- summarize_articles：读取本地 Markdown 文件，解析元信息并生成汇总摘要 Markdown 文件。

## 安装与运行

1. 安装依赖（推荐使用 Python 3.10+）

```bash
pip install -e .
# 或者
pip install fastmcp requests beautifulsoup4 markdownify PyYAML python-slugify
# 如需 headless（可选）
pip install playwright
playwright install
```

2. 运行（使用 stdio 传输）

```bash
wechat-oa-mcp-server
```

如需在 IDE/Agent 中注册为 MCP Server，请使用 stdio 方式启动。

## 工具说明

### read_wechat_articles
- 目的：批量读取 URL（形如 https://mp.weixin.qq.com/s/...），解析为 Markdown（顶端包含 YAML front matter），并保存到本地。
- 输入参数：
  - urls（string[]，必填）：文章链接列表。
  - fetch_strategy（auto|http|headless，默认 auto）：抓取策略；当前实现以 http 为主，遇到反爬可扩展到 headless。
  - output_dir（string，默认 exports/articles/）：输出目录。
  - filename_pattern（string，可选）：文件命名模式，如 `{date}_{title}.md`，支持 `{date}` `{title}` `{account_name}` 占位。
  - overwrite（boolean，默认 false）：是否覆盖同名文件。
  - concurrency（integer，默认 3）：并发抓取数（当前实现串行，后续可扩展）。
  - response_format（concise|detailed，默认 concise）：返回结果详细程度。
  - timeout_ms（integer，默认 10000）：单项抓取超时时间。
  - user_agent（string，可选）：自定义 UA。
- 输出结构：
  - written：成功写入文件的清单（url、saved_path、title、account_name、publish_time、preview）。
  - invalid：非法 URL 清单。
  - errors：错误清单（TIMEOUT、HTTP_ERROR、CHALLENGE、UNKNOWN）。
- Markdown 文件结构：
  - 顶部为 YAML front matter（键值对元信息块），随后空一行，再写正文。

YAML front matter 示例：

```yaml
---
title: 文章标题
account_name: 公众号名称
author: 作者名
publish_time: 2025-11-06T10:00:00+08:00
canonical_url: https://mp.weixin.qq.com/s/XXXX
source_url: https://mp.weixin.qq.com/s/XXXX
retrieved_at: 2025-11-06T23:59:00+08:00
article_id: weixin-XXXX
word_count: 1234
images: 5
---
```

### summarize_articles
- 目的：读取本地 Markdown 文件，解析元信息并生成摘要汇总文件。
- 输入参数：
  - input_paths（string|string[]，必填）：文件或目录路径；目录下递归查找 .md 文件。
  - pattern（string，默认 *.md）：glob 模式（当前版本以扩展名匹配为主）。
  - output_file（string，默认 exports/summaries/summary.md）：摘要输出文件路径。
  - include_metadata（boolean，默认 true）：是否在摘要文件顶部生成元信息汇总表。
  - summary_style（bullet|narrative|mixed，默认 bullet）：摘要风格。
  - language（zh|en，默认 zh）：摘要语言（当前实现对语言不做强约束）。
  - title（string，默认 文章摘要汇总）：摘要文件主标题。
- 输出结构：
  - output_file：生成的摘要文件路径。
  - count：成功解析的文章数量。
  - errors：解析错误列表。

摘要文件结构：
- 顶部可选生成“元信息清单”表格（标题/公众号/发布时间/链接）。
- 每篇文章一个二级标题，随后附来源、公众号、发布时间及摘要内容。

## 注意事项与扩展建议
- 反爬与动态加载：当前实现以 requests + BS4 为主。如遇反爬或需要渲染 JS，可安装 Playwright 并扩展 headless 策略。
- 文件命名：默认 `{title}.md`；如需避免重名，可在 filename_pattern 中加入 `{account_name}` 或 `article_id`。
- 容错策略：
  - publish_time 标准化失败时保留原始文本为 `publish_time_raw`。
  - YAML 解析失败时自动降级为“纯键值行”元信息格式。
- 法律与合规：请遵循目标网站的服务条款与爬虫政策，仅在合法授权范围内使用。

## 开发与测试
- 启动：`wechat-oa-mcp-server`（stdio）。
- 调用工具（示例 JSON）：

```json
{
  "name": "read_wechat_articles",
  "arguments": {
    "urls": ["https://mp.weixin.qq.com/s/xxxxxxxx"],
    "output_dir": "exports/articles",
    "filename_pattern": "{date}_{title}.md",
    "response_format": "detailed"
  }
}
```

```json
{
  "name": "summarize_articles",
  "arguments": {
    "input_paths": ["exports/articles"],
    "output_file": "exports/summaries/summary.md",
    "summary_style": "mixed",
    "include_metadata": true
  }
}
```

## 变更记录
- v0.1.0：初始实现，两工具方案，YAML front matter 强制。