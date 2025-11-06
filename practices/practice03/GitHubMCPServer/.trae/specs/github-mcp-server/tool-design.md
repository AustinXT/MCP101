# GitHub MCP Server 工具设计文档

## 工具选择与优先级

### 高优先级工具 (核心功能)

#### 1. `search_issues` - 搜索 Issues
**目的**: 让 Agent 能够搜索和发现相关的 Issues
**价值**: 核心的发现和调研功能

**输入参数**:
- `query` (string, required): 搜索查询字符串
- `repository` (string, optional): 限定特定仓库 (格式: owner/repo)
- `state` (string, optional): 状态过滤 (open, closed, all)
- `labels` (string, optional): 标签过滤
- `sort` (string, optional): 排序方式 (created, updated, comments)
- `order` (string, optional): 排序顺序 (asc, desc)
- `max_results` (number, optional): 最大返回结果数 (默认: 30)

**输出格式**: Markdown 表格格式
**响应选项**: concise (简要信息), detailed (完整信息)

#### 2. `list_pull_requests` - 列出拉取请求
**目的**: 查看仓库的 PRs 状态和详情
**价值**: 代码审查和合并状态跟踪

**输入参数**:
- `repository` (string, required): 目标仓库 (格式: owner/repo)
- `state` (string, optional): 状态过滤 (open, closed, all)
- `base_branch` (string, optional): 基础分支过滤
- `head_branch` (string, optional): 头部分支过滤
- `sort` (string, optional): 排序方式 (created, updated, popularity)
- `max_results` (number, optional): 最大返回结果数 (默认: 30)

**输出格式**: Markdown 表格格式
**响应选项**: concise (简要信息), detailed (完整信息)

#### 3. `get_file_content` - 获取文件内容
**目的**: 读取仓库中的文件内容
**价值**: 代码查看、配置读取、文档查阅

**输入参数**:
- `repository` (string, required): 目标仓库 (格式: owner/repo)
- `file_path` (string, required): 文件路径
- `ref` (string, optional): Git 引用 (分支、标签、提交)
- `format` (string, optional): 输出格式 (raw, markdown)

**输出格式**: 原始文本或格式化内容
**响应选项**: N/A (内容本身)

#### 4. `list_repository_contents` - 列出仓库内容
**目的**: 浏览仓库的文件和目录结构
**价值**: 项目结构探索和文件发现

**输入参数**:
- `repository` (string, required): 目标仓库 (格式: owner/repo)
- `path` (string, optional): 目录路径 (默认为根目录)
- `ref` (string, optional): Git 引用

**输出格式**: Markdown 列表格式
**响应选项**: concise (简要列表), detailed (完整信息)

### 中优先级工具 (增强功能)

#### 5. `get_issue_details` - 获取 Issue 详情
**目的**: 查看特定 Issue 的完整信息
**价值**: 详细的 Issue 分析和处理

**输入参数**:
- `repository` (string, required): 目标仓库
- `issue_number` (number, required): Issue 编号

**输出格式**: Markdown 格式的详细视图

#### 6. `get_pull_request_details` - 获取 PR 详情
**目的**: 查看特定 PR 的完整信息和更改
**价值**: 详细的代码审查和合并分析

**输入参数**:
- `repository` (string, required): 目标仓库
- `pull_number` (number, required): PR 编号

**输出格式**: Markdown 格式的详细视图

#### 7. `search_code` - 搜索代码
**目的**: 在代码库中搜索特定代码模式
**价值**: 代码查找和模式发现

**输入参数**:
- `query` (string, required): 代码搜索查询
- `repository` (string, optional): 限定特定仓库
- `language` (string, optional): 编程语言过滤

**输出格式**: Markdown 列表格式
**响应选项**: concise (简要结果), detailed (带代码片段)

### 低优先级工具 (高级功能)

#### 8. `get_user_repositories` - 获取用户仓库列表
**目的**: 查看用户或组织的仓库列表
**价值**: 项目发现和导航

**输入参数**:
- `username` (string, required): 用户名或组织名
- `type` (string, optional): 类型过滤 (all, owner, member, public, private)
- `sort` (string, optional): 排序方式 (created, updated, pushed, full_name)

#### 9. `check_rate_limit` - 检查速率限制状态
**目的**: 查看当前 API 速率限制状态
**价值**: 避免超出限制和优化请求

**输入参数**: None
**输出格式**: JSON 状态信息

## 工具协同关系

### 工作流示例

#### 代码审查工作流
1. `list_pull_requests` → 发现需要审查的 PRs
2. `get_pull_request_details` → 查看 PR 详情
3. `get_file_content` → 查看更改的文件内容
4. `search_issues` → 查找相关 Issues

#### Bug 调研工作流  
1. `search_issues` → 搜索相关的 bug reports
2. `get_issue_details` → 查看具体 Issue 详情
3. `get_file_content` → 查看相关代码文件
4. `list_repository_contents` → 探索项目结构

#### 项目发现工作流
1. `get_user_repositories` → 查看用户的仓库列表
2. `list_repository_contents` → 浏览感兴趣的项目
3. `search_issues` → 查看项目的活跃度

## 输入参数设计原则

### 命名约定
- 使用清晰的英文名称
- 避免缩写，除非是标准术语 (如 PR)
- 参数名称反映其用途

### 类型约束
- `string`: 文本输入，提供格式示例
- `number`: 数值输入，指定范围和默认值
- `enum`: 枚举值，提供可选值列表

### 验证规则
- 必需参数必须有清晰的错误提示
- 可选参数提供合理的默认值
- 格式验证 (如 repository 格式: owner/repo)

## 输出格式设计

### Markdown 优先
- 表格格式用于列表数据
- 代码块用于代码内容
- 标题和列表用于结构化信息

### 响应选项策略
- **concise**: 关键信息，适合概览
- **detailed**: 完整信息，适合深入分析
- 默认使用 concise 以节省 token

### 错误处理格式
- 清晰的错误消息
- 建议的修复步骤
- 相关的文档链接

## 工具注解设计

### `search_issues`
- `readOnlyHint`: true
- `openWorldHint`: true
- `idempotentHint`: true

### `list_pull_requests`  
- `readOnlyHint`: true
- `idempotentHint`: true

### `get_file_content`
- `readOnlyHint`: true
- `idempotentHint`: true

### `get_issue_details`
- `readOnlyHint`: true
- `idempotentHint`: true

## 速率限制考虑

### 工具级别的限制
- 搜索工具: 注意 30/分钟的限制
- 批量操作: 实现适当的延迟
- 错误处理: 清晰的速率限制错误信息

### 缓存策略
- ETag 支持条件请求
- 响应缓存以减少重复请求
- 本地缓存常用数据

## 安全性考虑

### 认证管理
- 环境变量存储访问令牌
- 不记录或暴露敏感信息
- 适当的权限范围

### 输入验证
- 验证 repository 格式
- 防止路径遍历攻击
- 限制文件大小请求

## 优先级排序理由

### 高优先级工具
1. **搜索功能**: Agent 最需要的发现能力
2. **内容访问**: 基本的代码和文件访问
3. **列表功能**: 导航和探索的基础

### 中优先级工具  
1. **详情查看**: 在发现后的深入分析
2. **代码搜索**: 更专业的开发需求

### 低优先级工具
1. **辅助功能**: 元数据和管理功能
2. **状态检查**: 运维相关的功能

## 后续扩展考虑

### 可能的未来工具
- `create_issue`: 创建新的 Issue
- `comment_on_issue`: 添加评论
- `review_pull_request`: 代码审查功能
- `merge_pull_request`: 合并 PR

### 集成扩展
- GitHub Actions 状态查看
- GitHub Projects 集成
- GitHub Packages 支持

## 评估指标

### 成功标准
- 工具覆盖主要使用场景
- 响应时间在可接受范围内
- 错误率低于 1%
- 用户满意度高

### 性能指标
- API 调用延迟
- 速率限制利用率  
- 缓存命中率
- 内存使用情况