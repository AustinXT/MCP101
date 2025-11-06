# GitHub MCP Server 规范

## 1. Server 概述

### 1.1 基本介绍
- **名称**: GitHub MCP Server
- **用途**: 集成 GitHub API，为 AI Agent 提供 GitHub 仓库访问能力
- **目标服务**: GitHub REST API v3
- **传输协议**: **stdio (标准输入输出)**
- **协议选择理由**: 主要用于本地开发和 Claude Desktop 集成，无需网络配置，提供最佳开发体验和性能

### 1.2 主要使用场景
1. **代码审查辅助**: 搜索 Issues、查看 PRs、获取文件内容
2. **项目调研**: 探索仓库结构、查看项目文档
3. **问题排查**: 搜索相关 Issues 和代码
4. **开发协作**: 查看项目状态和协作信息

### 1.3 核心价值
- **Agent-Centric**: 为 AI Agent 设计的工作流，而非简单 API 包装
- **上下文优化**: 返回高信号信息，避免数据转储
- **错误可操作**: 提供明确的错误指导和修复建议

## 2. 工具规范

### 2.1 高优先级工具

#### Tool: `search_issues`
**目的**: 搜索 GitHub Issues，支持多种过滤条件
**价值**: 核心的发现和调研功能

**输入 Schema**:
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "搜索查询字符串，支持 GitHub 搜索语法"
    },
    "repository": {
      "type": "string", 
      "description": "限定特定仓库，格式: owner/repo"
    },
    "state": {
      "type": "string",
      "enum": ["open", "closed", "all"],
      "description": "Issue 状态过滤"
    },
    "labels": {
      "type": "string",
      "description": "标签过滤，多个标签用逗号分隔"
    },
    "sort": {
      "type": "string", 
      "enum": ["created", "updated", "comments"],
      "description": "排序方式"
    },
    "order": {
      "type": "string",
      "enum": ["asc", "desc"], 
      "description": "排序顺序"
    },
    "max_results": {
      "type": "number",
      "minimum": 1,
      "maximum": 100,
      "description": "最大返回结果数，默认: 30"
    }
  },
  "required": ["query"]
}
```

**输出格式**: Markdown 表格
**响应选项**: 
- `concise`: 简要信息 (标题、状态、标签、创建时间)
- `detailed`: 完整信息 (包含描述、评论数等)

**错误处理**:
- `400`: 无效的搜索查询
- `404`: 仓库不存在
- `422`: 搜索语法错误
- `403`: 速率限制 exceeded

**Tool Annotations**:
- `readOnlyHint`: true
- `openWorldHint`: true  
- `idempotentHint`: true

---

#### Tool: `list_pull_requests`
**目的**: 列出仓库的拉取请求
**价值**: PR 状态跟踪和代码审查

**输入 Schema**:
```json
{
  "type": "object",
  "properties": {
    "repository": {
      "type": "string",
      "description": "目标仓库，格式: owner/repo",
      "required": true
    },
    "state": {
      "type": "string", 
      "enum": ["open", "closed", "all"],
      "description": "PR 状态过滤"
    },
    "base_branch": {
      "type": "string",
      "description": "基础分支过滤"
    },
    "head_branch": {
      "type": "string", 
      "description": "头部分支过滤"
    },
    "sort": {
      "type": "string",
      "enum": ["created", "updated", "popularity", "long-running"],
      "description": "排序方式"
    },
    "max_results": {
      "type": "number",
      "minimum": 1,
      "maximum": 100,
      "description": "最大返回结果数，默认: 30"
    }
  },
  "required": ["repository"]
}
```

**输出格式**: Markdown 表格
**响应选项**:
- `concise`: 简要信息 (标题、状态、分支、创建者)
- `detailed`: 完整信息 (包含描述、评论数、更改文件数)

**Tool Annotations**:
- `readOnlyHint`: true
- `idempotentHint`: true

---

#### Tool: `get_file_content`
**目的**: 获取仓库文件内容
**价值**: 代码查看和文档阅读

**输入 Schema**:
```json
{
  "type": "object",
  "properties": {
    "repository": {
      "type": "string",
      "description": "目标仓库，格式: owner/repo",
      "required": true
    },
    "file_path": {
      "type": "string", 
      "description": "文件路径，从仓库根目录开始",
      "required": true
    },
    "ref": {
      "type": "string",
      "description": "Git 引用 (分支、标签、提交哈希)"
    },
    "format": {
      "type": "string",
      "enum": ["raw", "markdown"],
      "description": "输出格式，默认: raw"
    }
  },
  "required": ["repository", "file_path"]
}
```

**输出格式**: 原始文本或格式化内容
**响应选项**: N/A (内容本身决定格式)

**错误处理**:
- `404`: 文件或仓库不存在
- `400`: 无效的文件路径
- `403`: 无访问权限

**Tool Annotations**:
- `readOnlyHint`: true
- `idempotentHint`: true

---

#### Tool: `list_repository_contents`
**目的**: 列出仓库目录内容
**价值**: 项目结构探索

**输入 Schema**:
```json
{
  "type": "object",
  "properties": {
    "repository": {
      "type": "string",
      "description": "目标仓库，格式: owner/repo", 
      "required": true
    },
    "path": {
      "type": "string",
      "description": "目录路径，默认为根目录"
    },
    "ref": {
      "type": "string",
      "description": "Git 引用"
    }
  },
  "required": ["repository"]
}
```

**输出格式**: Markdown 列表
**响应选项**:
- `concise`: 简要列表 (名称、类型、大小)
- `detailed`: 完整信息 (包含描述、更新时间等)

**Tool Annotations**:
- `readOnlyHint`: true
- `idempotentHint`: true

### 2.2 中优先级工具

#### Tool: `get_issue_details`
**目的**: 获取特定 Issue 详情
**输入**: `repository` (string, required), `issue_number` (number, required)
**输出**: Markdown 详细视图

#### Tool: `get_pull_request_details`  
**目的**: 获取特定 PR 详情
**输入**: `repository` (string, required), `pull_number` (number, required)
**输出**: Markdown 详细视图

#### Tool: `search_code`
**目的**: 搜索代码内容
**输入**: `query` (string, required), `repository` (string, optional), `language` (string, optional)
**输出**: Markdown 代码搜索结果

### 2.3 低优先级工具

#### Tool: `get_user_repositories`
**目的**: 获取用户仓库列表
**输入**: `username` (string, required), `type` (string, optional), `sort` (string, optional)
**输出**: Markdown 仓库列表

#### Tool: `check_rate_limit`
**目的**: 检查速率限制状态
**输入**: None
**输出**: JSON 状态信息

## 3. 共享基础设施

### 3.1 API 请求辅助函数
```python
def make_github_request(endpoint: str, params: dict = None) -> dict:
    """统一的 GitHub API 请求函数"""
    # 实现认证、错误处理、重试逻辑
    pass

def handle_rate_limit(response) -> bool:
    """处理速率限制"""
    pass
```

### 3.2 错误处理工具
```python
def create_error_response(error_type: str, message: str, details: dict = None) -> dict:
    """创建标准化的错误响应"""
    pass

def suggest_next_steps(error_type: str) -> list:
    """根据错误类型提供建议的下一步操作"""
    pass
```

### 3.3 响应格式化函数
```python
def format_issues_response(issues: list, concise: bool = True) -> str:
    """格式化 Issues 响应"""
    pass

def format_file_content(content: str, file_path: str, format_type: str) -> str:
    """格式化文件内容响应"""
    pass
```

### 3.4 分页辅助函数
```python
def handle_pagination(initial_response, max_items: int = 30):
    """处理 GitHub API 分页"""
    pass
```

## 4. 非功能需求

### 4.1 字符限制策略
- **默认限制**: 25,000 tokens
- **响应优化**: 自动截断过长的响应
- **格式选择**: 提供 concise/detailed 选项控制输出大小

### 4.2 速率限制处理
- **主动监控**: 实时检查速率限制状态
- **智能退避**: 指数退避重试机制
- **用户提示**: 清晰的速率限制错误信息

### 4.3 超时策略
- **API 超时**: 30秒 GitHub API 请求超时
- **工具超时**: 60秒工具执行超时
- **连接超时**: 10秒连接建立超时

### 4.4 大规模使用支持
- **连接池**: 复用 HTTP 连接
- **缓存策略**: 响应缓存减少重复请求
- **批量处理**: 优化多个工具调用

## 5. 部署配置

### 5.1 传输协议配置
```json
{
  "mcpServers": {
    "github-mcp": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxx",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

### 5.2 环境变量需求
- `GITHUB_TOKEN`: GitHub Personal Access Token (必需)
- `LOG_LEVEL`: 日志级别 (可选, default: "info")
- `CACHE_TTL`: 缓存时间 (可选, default: 300)

### 5.3 依赖列表
```txt
requests>=2.28.0
mcp>=0.1.0
python-dotenv>=0.19.0
```

### 5.4 安装配置
```bash
# 安装依赖
pip install requests mcp python-dotenv

# 设置环境变量
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# 运行服务器
python server.py
```

## 6. 评估场景

### 场景 1: 代码审查准备
1. `list_pull_requests` - 查看开放的 PRs
2. `get_pull_request_details` - 查看特定 PR 详情
3. `get_file_content` - 查看更改的文件
4. `search_issues` - 查找相关 Issues

### 场景 2: Bug 调研
1. `search_issues` - 搜索相关的 bug reports
2. `get_issue_details` - 查看具体 Issue
3. `get_file_content` - 查看相关代码文件
4. `list_repository_contents` - 探索项目结构

### 场景 3: 项目发现
1. `get_user_repositories` - 查看用户的仓库列表
2. `list_repository_contents` - 浏览项目结构
3. `search_issues` - 查看项目活跃度
4. `get_file_content` - 查看 README 文档

### 场景 4: 文档查阅
1. `list_repository_contents` - 查找文档目录
2. `get_file_content` - 阅读具体文档文件
3. `search_code` - 搜索相关代码示例

### 场景 5: 依赖分析
1. `get_file_content` - 查看 package.json/pyproject.toml
2. `search_issues` - 查找依赖相关 Issues
3. `search_code` - 搜索依赖使用情况

## 7. 完整性检查清单

### 规范完整性
- [x] 明确每个工具的目的和价值
- [x] 包含详细的输入/输出设计  
- [x] 定义清晰的错误处理策略
- [x] 考虑 Agent 的上下文限制
- [x] 提供真实的使用场景
- [x] 遵循 MCP 最佳实践
- [x] 明确传输协议选择及理由
- [x] 包含部署配置说明

### 技术可行性
- [x] API 端点验证完成
- [x] 认证机制设计完成
- [x] 速率限制处理方案
- [x] 错误处理策略制定
- [x] 性能优化考虑

### 用户体验
- [x] 工具命名反映任务
- [x] 响应格式优化
- [x] 错误信息可操作
- [x] 使用场景覆盖全面

## 8. 后续开发计划

### 短期目标 (v1.0)
- [ ] 实现高优先级工具
- [ ] 完成基础错误处理
- [ ] 集成速率限制监控
- [ ] 提供完整的文档

### 中期目标 (v1.1)
- [ ] 实现中优先级工具
- [ ] 添加响应缓存
- [ ] 优化性能指标
- [ ] 增强测试覆盖

### 长期目标 (v1.2+)
- [ ] 实现低优先级工具
- [ ] 支持更多 GitHub 功能
- [ ] 添加高级配置选项
- [ ] 提供扩展插件机制