# 工具设计（WechatOAMCPServer，两工具方案）

本文档定义 WechatOAMCPServer 的工具级设计与实现细节，确保与规范一致并便于后续维护与扩展。该服务器基于 Python FastMCP 框架实现，采用 stdio 传输，提供两类核心工具：
- read_wechat_articles：读取微信公众号文章并转换为符合规范的 Markdown 文件（强制包含顶部元信息块）。
- summarize_articles：读取本地 Markdown 集合并生成汇总摘要 Markdown 文件。

1. 设计原则与框架约定
- 采用 FastMCP 的 @mcp.tool 装饰器注册工具，函数签名和类型提示决定工具 Schema。
- 输入验证采用 Pydantic v2（建议在后续迭代将内部 dict 入参替换为 BaseModel）。
- I/O 操作优先使用 async/await；当前版本允许同步实现，但在高并发和网络操作上建议迁移到 httpx.AsyncClient 与 anyio.to_thread。
- 默认使用 stdio 传输；后续若需网络访问可切换 transport="http" 并配置 host/port。
- 所有生成的 Markdown 文件在文件顶部必须写入“元信息 front matter”，随后空一行，再写正文内容；优先使用 YAML front matter，回退到 key: value 行。

2. 工具：read_wechat_articles（读取并导出 Markdown）
2.1 输入参数
- urls: list[str]（必填）—— 微信公众号文章 URL 列表，形如 https://mp.weixin.qq.com/s/...
- fetch_strategy: Literal["auto","http","headless"]（默认 auto）—— 抓取策略；auto 遇到反爬回退到 headless。
- output_dir: str（默认 exports/articles/）—— 输出目录。
- filename_pattern: str（可选）—— 文件命名模式，支持占位 {date}、{title}、{account_name}。
- overwrite: bool（默认 false）—— 同名是否覆盖。
- concurrency: int（默认 3）—— 并发数（当前实现按分片串行处理，后续可改为真正并发）。
- response_format: Literal["concise","detailed"]（默认 concise）—— 返回结果详细程度。
- timeout_ms: int（默认 10000）—— 单项抓取超时时间。
- user_agent: str（可选）—— 自定义 UA。

2.2 处理流程（算法）
- 预校验 URL：必须以 https://mp.weixin.qq.com/s 开头，否则标记 INVALID_URL。
- 抓取策略：
  - http：使用 requests 直连获取 HTML；必要时附加 UA/超时。
  - headless（预留）：基于 Playwright 渲染并抓取。
  - auto：先 http；检测到挑战/异常时可回退 headless（当前版本保留占位）。
- HTML 解析（BeautifulSoup）：
  - 标题：#activity-name 或 meta[property="og:title"]
  - 账号名：#js_name 或 meta[name="publisher"]
  - 作者：.rich_media_meta_list .rich_media_meta_text（尽力而为）
  - 发布时间：#publish_time 或 meta[property="article:published_time"]；尽量标准化为 ISO-8601，失败保留原始。
  - 正文：#js_content 容器的 innerHTML；无则用全文。
  - 图片：#js_content img 的 data-src/src 计数。
- Markdown 转换：优先使用 markdownify；失败回退到纯文本。
- 元信息 front matter（强制）：
  - 字段：title, account_name, author, publish_time, canonical_url, source_url, retrieved_at, article_id, word_count, images, 可选 publish_time_raw。
  - 写入格式：优先 YAML（PyYAML），回退为 key: value 行。
- 文件命名：
  - 默认：{title}.md，清理非法字符。
  - 自定义：替换占位 {date}（YYYYMMDD）、{title}、{account_name}（slug）。
  - 冲突：overwrite=false 时自动加后缀 _2、_3...
- 返回结果：summary 与逐项 items 列表（见 2.4）。

2.3 错误与容错
- INVALID_URL：非法链接；继续处理其他 URL。
- CHALLENGE：反爬挑战；建议启用 headless 或降低并发（当前版本返回提示）。
- TIMEOUT：超时；建议增大 timeout_ms 或重试。
- WRITE_ERROR：文件写入失败；建议检查路径/权限。
- NOT_FOUND：内容缺失或被删除；建议替换 URL。

2.4 输出结构（JSON）
- summary: { total, succeeded, failed }
- items: [
  { url, saved_path, title?, account_name?, bytes_written, duration_ms?, status: "ok"|"error", error_code?, hint?, preview_snippet? }
]

3. 工具：summarize_articles（汇总摘要生成）
3.1 输入参数
- files: list[str]（可选）—— 指定的 Markdown 文件路径列表。
- input_dir: str（可选）—— 输入目录，用于与 glob 组合匹配。
- glob: str（默认 **/*.md）—— 相对 input_dir 的匹配模式，支持 fnmatch。
- output_path: str（默认 exports/summaries/summary_{date}.md）—— 输出文件路径。
- style: Literal["key_points","outline","narrative","brief"]（默认 key_points）—— 摘要风格。
- language: Literal["zh","en","auto"]（默认 auto）—— 输出语言与标签（如 “来源/账号/发布时间”）。
- per_article_max_chars: int（可选）—— 每篇最大字符数，超出截断并标注。
- include_toc: bool（默认 true）—— 生成基于标题的目录。
- include_metadata: bool（默认 true）—— 每节保留来源文件名与原始链接（若前言块可解析）。
- response_format: Literal["concise","detailed"]（默认 concise）。

3.2 处理流程（算法）
- 构建文件集合：
  - 若 files 非空，直接使用；
  - 否则在 input_dir 下按 glob 匹配，忽略不可读文件。
- 解析 front matter：
  - 优先解析 YAML；
  - 回退解析 key: value 行；
  - 缺失字段以空字符串或占位符处理（如 Unknown）。
- 按 style 生成摘要：
  - key_points：条目式要点；
  - outline：分节大纲；
  - narrative：简述；
  - brief：超短摘要。
- 语言标签：根据 language 切换“来源/账号/发布时间”等标签；auto 可根据内容或环境选择。
- 输出 Markdown：顶部可选目录；每篇摘要块包含标题、来源、账号、发布时间；尾部可选 metadata manifest。
- 写文件并返回结果。

3.3 错误与容错
- FILE_NOT_FOUND / EMPTY_INPUT：未匹配到任何 Markdown 文件。
- READ_ERROR：读文件失败（权限/编码）。
- WRITE_ERROR：输出失败。
- TOO_LONG：超出 token 预算，建议 brief 或调小 per_article_max_chars。

3.4 输出结构（JSON）
- { saved: true|false, path, bytes_written, article_count, warnings?: [], errors?: [], sections_overview?, preview_snippet? }

4. Front Matter（强制）与解析要求
- 结构：文件顶部 front matter（YAML 优先）→ 空行 → 正文。
- 必填字段：title, account_name, publish_time（可空但字段名保留）, canonical_url, source_url, retrieved_at, article_id, word_count, images。
- 兼容性：若 YAML 写入失败，回退为 key: value 行，summarize_articles 仍需解析。
- summarize_articles 必须解析该前言块，若缺失字段则以空或 Unknown 处理，并可在汇总尾部生成 metadata manifest（列表化所有文章的元信息）。

5. 文件命名与目录结构
- 导出目录默认 exports/articles/；汇总目录默认 exports/summaries/。
- 文件名占位：{date}（YYYYMMDD）、{title}（清理非法字符）、{account_name}（slug）。
- 冲突处理：overwrite=false 时添加后缀 _2、_3...

6. 测试与示例场景
- 3 个合法 URL 成功导出；1 个非法 URL 报错但不影响其他项。
- auto 策略遇到挑战；返回 CHALLENGE 提示。
- summarize_articles 对目录 **/*.md 汇总，style=outline，language=en 输出英文摘要。
- 缺失或非 YAML 的 front matter 仍能被解析并汇总。

7. 未来扩展建议
- 将 read_wechat_articles 的网络操作迁移到 httpx.AsyncClient 并支持真正并发。
- headless 策略使用 Playwright；提供启用/禁用开关与重试退避策略。
- 输入 Pydantic 模型化，确保更严格的类型与 schema 暴露。
- 国际化标签与多语言摘要风格优化。

本文档作为实现参照，应与 spec.md 的规范保持一致，并在变更时同步更新。