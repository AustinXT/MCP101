# 微信公众号（mp.weixin.qq.com）文章内容访问——API 调研

概述
- 微信公众号文章为公开网页，通常位于 https://mp.weixin.qq.com/s/....
- 官方未提供公开、稳定的文章内容 API；实践上通过 HTTP 获取页面并解析 HTML 获取内容。
- 平台存在反爬与动态渲染机制。需要现代浏览器 User-Agent、适度的并发与重试策略；当静态请求失败时，建议使用无头浏览器（如 Playwright）。

访问方法
- 直接 HTTP GET 文章 URL（https://mp.weixin.qq.com/s/<slug>）
  - 常见选择器与结构：
    - 标题：#activity-name
    - 账号/作者：#js_name 或相关 meta 标签
    - 发布时间：#publish_time
    - 正文容器：#js_content
    - 图片多使用 data-src 属性
  - 优点：简单快速，依赖少。
  - 缺点：易触发反爬检查，部分内容由 JS 注入，偶尔需要携带 Cookie。
- 无头浏览器渲染（Playwright/Selenium）
  - 模拟真实浏览器，渲染动态内容，提升对反爬的鲁棒性。
  - 当 GET 返回验证码/挑战页、内容截断或异常重定向时，建议切换到 headless。
- 非公开内部接口（仅供了解，不建议依赖）
  - mp/getappmsgext：获取文章阅读/点赞等扩展信息，需 appmsg_token、__biz 等参数，通常依赖客户端上下文或 MITM，不适合通用生产方案。
  - mp/getmasssendmsg：某账号历史推送列表，参数会话相关且脆弱。

认证与授权
- 公共文章一般无需认证。
- 反爬可能要求现代 UA 与稳定的 Cookie/会话。
- 无官方 API key 或 OAuth 流程用于文章内容获取。

速率限制与约束
- 无公开的服务端限速规则，但频繁或并行请求可能被封禁。
- 推荐客户端策略：
  - 并发上限（如 3–5）
  - 429/403 或挑战页使用指数退避（含随机抖动）
  - 现代 UA 与必要时的代理支持
  - 尊重法律与平台条款

错误与处理
- 常见失败：
  - 403/429 或挑战页（验证码）
  - 404（文章删除或不可访问）
  - HTML 布局变化导致选择器失效
  - 内容截断、图片链接使用 data-src
- 处理建议：
  - 重试并回退到 headless 渲染
  - 文本提取采用保守策略（可回退到可见文本节点）
  - 输出可操作错误提示（建议 headless、校验 URL、降低并发等）

数据模型（文章内容）
- canonical_url（规范化链接）
- title（标题）
- account_name（账号展示名）与可能的账号标识（如 __biz）
- author（若可用）
- publish_time（尽可能标准化为 ISO-8601）
- content_html（原始 HTML）、content_markdown（转换后）、content_text（纯文本）
- images（图片 URL 列表）、视频/iframe（若存在）
- 引用与外链

限制与注意
- HTML 结构可能变化；需弹性选择器与版本化维护。
- 局部内容可能受区域/设备限制；即便 headless 也可能失败。
- 合规：确保使用符合适用法律与平台政策。

参考资料（社区实践，非官方文档）
- wechat-article-scraper（关于 getappmsgext 等内部端点）：https://github.com/vinceyyy/wechat-article-scraper
- 50 行代码爬取公众号文章（参数与方法示例）：https://www.codestudyblog.com/cnb08/0812112704.html
- Selenium 抓取示例项目：
  - https://github.com/chocoluffy/wechat_web_scraper
  - https://github.com/Ziheng-Liang/wechat_web_scraper

以上资料用于理解技术约束与实践要点，不代表官方 API。请以稳健的 HTML 解析与 headless 回退为主要方案。