# MCP 服务器规范——WechatOAMCPServer（两工具方案更新）

更新说明
- 在不改变服务器概述与传输协议选择（stdio）的前提下，工具集简化为两工具方案：
  1) read_wechat_articles：批量读取微信公众号文章并转换为 Markdown，逐一保存到本地。
  2) summarize_articles：读取本地 Markdown 文章集合，生成一个汇总摘要的 Markdown 文件并保存到本地。
- 此更新旨在降低 Agent 的认知负担与上下文占用，提供一站式工作流。原有多工具设计（单篇读取、单篇摘要、批量摘要、URL 校验、纯文本等）在本项目中不再推荐使用。

4.2A 工具规范（两工具方案）

工具：read_wechat_articles
- 目的：批量读取 URL，解析并转换为 Markdown，并按命名规则保存到本地目录。
- 输入（Input Schema）：
  - urls（string[]，必填）：形如 `https://mp.weixin.qq.com/s/...` 的文章链接列表。
  - fetch_strategy（enum：auto|http|headless，默认 auto）：抓取策略；auto 下遇到反爬自动回退到 headless。
  - output_dir（string，可选，默认 `exports/articles/`）：输出目录（相对项目或绝对路径）。
  - filename_pattern（string，可选，如 `{date}_{title}.md`）：未提供时使用 `{title}.md`，自动清理非法字符；同名冲突自动加后缀。
  - overwrite（boolean，可选，默认 false）：是否覆盖同名文件。
  - concurrency（integer，可选，默认 3）：并发抓取数（建议 3–5）。
  - response_format（enum：concise|detailed，默认 concise）：返回结果详细程度；concise 为精简清单，detailed 附预览片段。
  - timeout_ms（integer，可选，默认 10000）：单项抓取超时时间。
  - user_agent（string，可选）：自定义 UA。

Markdown 文件结构与元信息格式（强制）
- 所有输出的 Markdown 文件，必须在文件最上方包含“键值对元信息块（front matter）”，随后空一行，再写入正文内容。
- 推荐使用 YAML front matter 语法，示例如下：

```
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

正文从这里开始……
```

- 字段获取与容错：
  - title：`#activity-name` 或等价选择器；缺失时用文件名代替。
  - account_name：`#js_name` 或 meta；不可得时置空并记录 `account_name_raw`。
  - author：可选；缺失不报错。
  - publish_time：尽量标准化为 ISO-8601，失败时保留原始并另存 `publish_time_raw`。
  - canonical_url / source_url：分别保存规范化与原始链接。
  - retrieved_at：生成文件时的时间戳（ISO-8601）。
  - article_id：基于 slug/hash；用于去重与引用。
  - word_count / images：从正文统计；图片以标准化链接计数。

- 兼容格式：
  - 若无法写入 YAML，则允许使用“Key: Value”逐行的元信息块；解析端仍应优先尝试 YAML。
- 输出（Output Format）：JSON
  - summary：{ total, succeeded, failed }
  - items：[{ url, title?, path, bytes_written, duration_ms, status: 'ok'|'error', error_code?, hint?, preview_snippet? }]
- 错误处理（Error Handling）：
  - INVALID_URL：提示使用 `mp.weixin.qq.com/s/...`；下一步：修正 URL 或剔除异常项。
  - CHALLENGE（反爬挑战）：建议设置 `fetch_strategy=headless` 或保持 auto；下一步：重试并降低并发。
  - TIMEOUT：建议增大 `timeout_ms` 或重试；下一步：对特定 URL 单独抓取。
  - WRITE_ERROR（路径/权限）：建议调整 `output_dir` 或授予权限；下一步：改用可写目录。
  - NOT_FOUND：文章可能已删除；下一步：替换 URL 或跳过。
- 工具注记（Tool Annotations）：
  - readOnlyHint：false（涉及写文件）
  - destructiveHint：true（文件系统写入）
  - idempotentHint：false（若使用时间戳或自动后缀，重复调用结果不同）
  - openWorldHint：true（访问外部网页）

工具：summarize_articles
- 目的：从本地 Markdown 文章集合（文件列表或目录+glob）生成一个汇总摘要的 Markdown 文件并落盘保存。
- 输入（Input Schema）：
  - files（string[]，可选）：Markdown 文件路径列表。
  - input_dir（string，可选）：输入目录；若提供则与 `glob` 组合匹配文件。
  - glob（string，可选，默认 `**/*.md`）：文件匹配模式（相对 `input_dir`）。
  - output_path（string，可选，默认 `exports/summaries/summary_{date}.md`）：汇总摘要输出文件路径。
  - style（enum：key_points|outline|narrative|brief，默认 key_points）：摘要风格。
  - language（enum：zh|en|auto，默认 auto）：摘要语言；auto 自动识别并选择合适语言。
  - per_article_max_chars（integer，可选）：每篇输入最大字符数，用于控 token；超出部分截断并标记。
  - include_toc（boolean，可选，默认 true）：是否在汇总文件顶部生成目录（按文章标题）。
  - include_metadata（boolean，可选，默认 true）：是否在每篇摘要块中保留来源文件名与原始链接（若可解析）。
  - response_format（enum：concise|detailed，默认 concise）：返回结果详细程度；detailed 可返回片段预览。
- 输出（Output Format）：JSON
  - `{ saved: true|false, path, bytes_written, article_count, warnings?: [], errors?: [], sections_overview?, preview_snippet? }`
- 错误处理（Error Handling）：
  - FILE_NOT_FOUND / EMPTY_INPUT：未找到任何 Markdown 文件；下一步：检查 `files` 或 `input_dir+glob`。
  - READ_ERROR（读文件失败）：提示权限或编码问题；下一步：更换路径或修复编码。
  - WRITE_ERROR（输出失败）：提示路径/权限；下一步：修改 `output_path`。
  - TOO_LONG（超出 token 预算）：建议减少 `per_article_max_chars` 或选择 `brief` 风格。
- 工具注记（Tool Annotations）：
  - readOnlyHint：false（写输出文件）
  - destructiveHint：true（文件系统写入）
  - idempotentHint：false（摘要可能非严格确定性；文件名包含日期时重复执行结果不同）
  - openWorldHint：false（纯本地文件操作）

工作流示例
- 方案 A：read_wechat_articles（urls→MD 文件）→ summarize_articles（MD 集合→汇总摘要 MD）
- 方案 B：仅执行 read_wechat_articles，用于生成规范化的 Markdown 语料库。

附：评估场景（两工具方案，10 个）
1) read_wechat_articles：给定 3 个合法 URL，成功生成 3 个 Markdown 文件并返回 items 清单（concise）。
2) read_wechat_articles：其中 1 个 URL 非法，2 个成功；返回该项 INVALID_URL，总体继续处理。
3) read_wechat_articles：遇到反爬挑战，auto 模式回退到 headless 并成功保存；返回 CHALLENGE 提示。
4) read_wechat_articles：output_dir 无写权限，返回 WRITE_ERROR；修改为可写目录后成功。
5) read_wechat_articles：超时场景，增大 timeout_ms 后成功；返回 TIMEOUT 并建议退避重试。
6) summarize_articles：从 `exports/articles/` 按 glob 读取所有 MD，生成汇总摘要文件并保存；返回 article_count 与 path。
7) summarize_articles：style=outline，language=en，生成英文大纲式摘要；检查 sections_overview。
8) summarize_articles：部分 MD 文件存在编码或格式异常，返回 READ_ERROR/warnings 并继续其他文件。
9) summarize_articles：设置 per_article_max_chars 控制每篇输入长度，防止超出 token 预算；返回 truncated 标记。
10) 两工具串联：先批量生成 MD，再汇总生成最终摘要；重复执行在 overwrite=false 下产生不同文件名后缀，标注非幂等。

4.1 服务器概述
- 名称：WechatOAMCPServer
- 目的：根据用户提供的微信公众号文章 URL，读取并解析内容，输出高信号的 Markdown 摘要，适配有限的上下文窗口。
- 目标服务：mp.weixin.qq.com 公共文章页面
- 主要使用场景：
  - 单篇：给定 URL → 抓取解析 → 摘要为 Markdown → 下游推理/报告。
  - 批量：多 URL → 并发读取 → 合并输出 Markdown 报告，包含逐项状态。
- 传输协议：stdio
  - 理由：本地、单用户工作流；部署简单；便于管理 headless 依赖；无需远程暴露。

4.2 工具规范
- read_wechat_article
  - 目的：抓取并解析文章内容，返回结构化数据；屏蔽反爬复杂性。
  - 输入：
    - url（string，必填）：如 https://mp.weixin.qq.com/s/XXXX
    - fetch_strategy（auto|http|headless，默认 auto）
    - include（object，可选）：{ raw_html?, markdown?, images?, links? }
    - response_format（concise|detailed，默认 concise）
    - timeout_ms（int，可选，默认 10000）
    - user_agent（string，可选）
  - 输出（JSON）
    - concise：canonical_url, title, account_name, author, publish_time, content_text
    - detailed：content_markdown/raw_html/images[]/links[]（按需）
  - 错误处理：
    - INVALID_URL：提示规范 URL 格式与下一步使用 validate
    - CHALLENGE：建议 headless 并重试
    - TIMEOUT：建议增大 timeout_ms 与退避重试
    - NOT_FOUND：提示可能被删除，建议更换 URL
  - 注记：readOnlyHint=true；destructiveHint=false；idempotentHint=true；openWorldHint=true

- batch_summarize_to_markdown
  - 目的：批量生成合并的 Markdown 报告，提供并发与错误控制。
  - 输入：
    - urls（string[]，必填）
    - style/language（同上）
    - per_item_response_format（concise|detailed，默认 concise）
    - concurrency（int，默认 3）
    - on_error（continue|abort，默认 continue）
  - 输出：Markdown 报告（分节）；detailed 模式附逐项 JSON 状态与耗时。
  - 错误处理：逐项返回提示；在 429/403 时建议降低 concurrency。
  - 注记：readOnlyHint=true；destructiveHint=false；idempotentHint=false；openWorldHint=true

4.3 共享基础设施
- HTTP 抓取：可配置 UA、重试、退避、代理支持。
- Headless 渲染：基于 Playwright，等待 DOM 与选择器捕获。
- HTML 解析：弹性选择器与版本化；图片 data-src 归一化。
- Markdown 转换：HTML→Markdown 清洗、引用块、链接保留。
- 错误处理工具：统一错误码、提示与下一步建议。
- 批量与并发：并发上限、逐项聚合与状态报告。
- Token 管理：截断、摘要长度控制。
- 缓存（可选）：URL→内容缓存，减少重复抓取。

4.4 非功能需求
- Token：默认 25,000；支持截断与 concise 输出。
- 限速：并发上限与指数退避（429/403）。
- 超时：默认 10s，可配置。
- 扩展性：批量工具支持成百上千 URL，受并发与内存管理约束。
- 鲁棒性：选择器版本化；当 HTML 改动时回退到纯文本。

4.5 部署配置
- 传输：stdio
- 环境变量：
  - WECHATOA_USER_AGENT（可选）
  - WECHATOA_TIMEOUT_MS（可选）
  - WECHATOA_MAX_CONCURRENCY（可选）
  - WECHATOA_PROXY（可选）
  - WECHATOA_HEADLESS_ENABLED（默认 true）
  - WECHATOA_EXPORT_DIR（默认 exports/）
- 依赖建议：requests/httpx、lxml/BeautifulSoup、Playwright（可选）、html2text/Readability 风格转换器。
- HTTP 备选（若未来启用）：Host 0.0.0.0，Port 8088，Base Path /mcp/wechat-oa。

4.6 评估场景（10 个）
- 单 URL 静态抓取成功，输出简版要点。
- 单 URL 触发反爬，自动切换 headless 并成功解析。
- 超长文章，target_length=short 保持在 token 预算内。
- 多图片 data-src 归一化，detailed 模式包含图片引用。
- 非法域名 URL，validate 返回可操作错误。
- 5 个 URL 批量，其中一个 404，继续并返回逐项状态。
- 仅需元数据，走快捷路径。
- 仅需纯文本，max_chars=10000，返回截断标记。
- 导出 Markdown 到指定路径，模拟权限错误后重试成功。
- 混合语言文章，language=auto 自动选择并保留中文标题与英文摘要。

参考
- 无官方 API：依赖公共页面与稳健解析。
- 社区实践：
  - https://github.com/vinceyyy/wechat-article-scraper
  - https://github.com/chocoluffy/wechat_web_scraper
  - https://github.com/Ziheng-Liang/wechat_web_scraper
  - https://www.codestudyblog.com/cnb08/0812112704.html