# GitHub MCP Server

一个用于与 GitHub API 交互的 Model Context Protocol (MCP) 服务器，基于 Python FastMCP 构建。

## 特性（Features）

- 搜索 Issues：跨仓库进行问题搜索并支持高级筛选
- 列出 Pull Requests：查看指定仓库的 PR 列表
- 获取 Issue 详情：查看单个 Issue 的详细信息
- 获取 Pull Request 详情：查看单个 PR 的详细信息
- 搜索代码：支持按关键字、限定 filename/extension/path，并可按仓库范围搜索
- 获取文件内容：从 GitHub 仓库中读取文件内容
- 浏览仓库目录：列出仓库路径下的文件/目录结构
- 多种响应格式：JSON（结构化数据）、Markdown（可读性好）
- 细粒度信息级别：concise（摘要）与 detailed（详细）
- 统一工具注册：工具模块为纯函数 + 元数据，集中在 server 中注册到单一 FastMCP 实例
- 可选内存缓存：提供简单 TTL 缓存工具，便于只读接口的性能优化

## 安装（Installation）

### 前置条件

- Python 3.10 或更高版本
- GitHub Personal Access Token（可选但推荐，用于更高的速率限制）

### 安装步骤

1. 克隆或下载本项目
2. 安装依赖：
   ```bash
   pip install -e .
   ```
3. 配置环境变量：
   ```bash
   cp .env.example .env
   ```
   编辑 `.env`：
   ```env
   GITHUB_TOKEN=your_github_personal_access_token_here
   LOG_LEVEL=INFO
   CACHE_TTL=300
   API_TIMEOUT=30
   MAX_RESULTS=100
   ```
4. 生成 GitHub Token（如需访问私有仓库或提高速率限制）：
   - GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - 建议选择 `repo` scope（以便访问私有仓库）

## 使用（Usage）

### 与 Claude Desktop 配合使用

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": [
        "-m",
        "github_mcp_server.server"
      ],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

然后重启 Claude Desktop。

### 使用 FastMCP CLI

1. 安装 FastMCP：
   ```bash
   pip install fastmcp
   ```
2. 开发模式运行：
   ```bash
   fastmcp dev src/github_mcp_server/server.py
   ```
   这将启动 MCP Inspector（一般在 http://localhost:5173）并提供调试界面。
3. 直接运行：
   ```bash
   python -m github_mcp_server.server
   ```

## 可用工具（Available Tools）

### search_issues
搜索 GitHub Issues（支持筛选、排序等）。

```python
search_issues(
    query="bug in auth",
    format="json",
    detail="concise",
    limit=10,
    sort="created",
    order="desc"
)
```

### list_pull_requests
列出指定仓库的 Pull Requests。

```python
list_pull_requests(
    repository="facebook/react",
    state="open",
    format="markdown",
    detail="detailed",
    limit=20
)
```

### get_issue_details
获取单个 Issue 的详细信息。

```python
get_issue_details(
    repository="facebook/react",
    issue_number=123,
    format="json",
    detail="concise"
)
```

### get_pull_request_details
获取单个 Pull Request 的详细信息。

```python
get_pull_request_details(
    repository="microsoft/vscode",
    pull_number=42,
    format="markdown",
    detail="detailed"
)
```

### search_code
在 GitHub 上搜索代码（可选按仓库范围）。

```python
search_code(
    query="filename:README.md",
    repository="facebook/react",  # 可选
    format="json",
    detail="concise",
    limit=10
)
```

### get_file_content
获取仓库中的文件内容。

```python
get_file_content(
    repository="microsoft/vscode",
    path="README.md",
    ref="main",
    format="json"
)
```

### list_repository_contents
浏览仓库目录结构。

```python
list_repository_contents(
    repository="torvalds/linux",
    path="drivers",
    recursive=True,
    format="markdown"
)
```

## 响应格式（Response Formats）

### JSON
适用于程序化处理：

```json
{
  "total_count": 42,
  "items": [
    {
      "title": "Bug in authentication",
      "state": "open",
      "html_url": "https://github.com/owner/repo/issues/123"
    }
  ]
}
```

### Markdown
适用于人类阅读：

```markdown
## Search Results (42 items)

### Bug in authentication
- **State**: open
- **URL**: https://github.com/owner/repo/issues/123
- **Created**: 2023-01-15T10:30:00Z
```

## 错误处理（Error Handling）

- 认证错误：检查 GITHUB_TOKEN 环境变量
- 速率限制：适当等待或使用 Token 提升限制
- 参数校验：检查输入参数是否符合要求
- 网络错误：检查网络连接

## 开发（Development）

### 目录结构（Project Structure）

```
GitHubMCPServer/
├── src/
│   └── github_mcp_server/
│       ├── server.py          # 主服务文件（统一工具注册）
│       ├── tools/             # 工具实现（纯函数 + 元数据）
│       │   ├── search_issues.py
│       │   ├── list_pull_requests.py
│       │   ├── get_issue_details.py
│       │   ├── get_pull_request_details.py
│       │   ├── search_code.py
│       │   ├── get_file_content.py
│       │   └── list_repository_contents.py
│       ├── utils/             # 通用工具
│       │   ├── api_client.py
│       │   ├── cache.py
│       │   ├── errors.py
│       │   └── formatters.py
├── pyproject.toml             # 项目配置
├── requirements.txt           # 依赖
├── .env.example               # 环境变量模板
└── README.md                  # 项目文档
```

### 新增工具（Adding New Tools，统一注册模式）

采用“函数 + 元数据”的模式，在 `server.py` 中统一注册：

1. 在 `src/github_mcp_server/tools/` 下创建新文件（例如 `your_tool.py`）
2. 定义 Pydantic 输入模型与异步函数：
   ```python
   class YourToolInput(BaseModel):
       ...

   async def your_tool(input: YourToolInput) -> str:
       ...
   ```
3. 在模块中导出 `TOOL_ANNOTATIONS`：
   ```python
   TOOL_ANNOTATIONS = {
       "readOnlyHint": True,
       "idempotentHint": True,
       "openWorldHint": False,
   }
   ```
4. 在 `src/github_mcp_server/server.py` 中使用 `importlib.import_module` 导入新工具模块，并加入 `tools_to_register` 列表：
   ```python
   import importlib
   your_tool_mod = importlib.import_module("github_mcp_server.tools.your_tool")

   tools_to_register = [
       # ... existing tools
       (your_tool_mod, "your_tool"),
   ]
   ```
5. 运行服务并查看日志，出现 `Registered tool: your_tool` 即表示注册成功。

### 测试（Testing）

使用 FastMCP 的 dev 模式进行交互式测试：

```bash
fastmcp dev src/github_mcp_server/server.py
```

## 配置（Configuration）

### 环境变量（Environment Variables）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `GITHUB_TOKEN` | 可选 | GitHub Personal Access Token（推荐设置，以获得更高的速率限制；未认证请求限制为 60/小时） |
| `LOG_LEVEL` | `INFO` | 日志级别（DEBUG, INFO, WARNING, ERROR） |
| `CACHE_TTL` | `300` | 缓存 TTL（秒） |
| `API_TIMEOUT` | `30` | API 请求超时（秒） |
| `MAX_RESULTS` | `100` | 单次请求的最大返回条数 |

### 速率限制（Rate Limits）

- 认证请求：5000 次/小时
- 未认证请求：60 次/小时
- 服务会在触发限制时提供清晰的提示信息

### 缓存（Caching）

- 在 `src/github_mcp_server/utils/cache.py` 中提供了简单的内存缓存（TTL）工具
- 可在工具函数或 API 调用处按需使用 `cache_get`、`cache_set`、`cache_clear`
- 默认服务不启用全局缓存，可对读取频繁的接口选择性启用

## 许可证（License）

MIT License（请参阅 LICENSE 文件）

## 支持（Support）

- 使用问题与反馈：请在仓库 Issue 中提交
- 参考资料：MCP 协议文档、FastMCP 文档、GitHub REST API 文档