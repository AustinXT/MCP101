# GitHub API 调研文档

## 概述
GitHub REST API v3 提供了对 GitHub 平台数据的完整访问，包括仓库、问题、拉取请求、文件内容等。

## 认证方式

### 1. 个人访问令牌 (Personal Access Token)
- **速率限制**: 5,000 请求/小时 (认证用户)
- **权限范围**: 可配置细粒度权限
- **安全性**: 需要安全存储令牌

### 2. 未认证访问
- **速率限制**: 60 请求/小时 (基于 IP)
- **限制**: 只能访问公开数据

### 3. GitHub App 认证
- **速率限制**: 5,000-15,000 请求/小时 (根据组织规模)
- **适用场景**: 企业级应用

## 关键端点

### 搜索相关端点

#### 搜索 Issues
- **端点**: `GET /search/issues`
- **参数**: `q` (查询字符串), `sort`, `order`, `per_page`, `page`
- **速率限制**: 30 请求/分钟 (认证), 10 请求/分钟 (未认证)
- **示例查询**: 
  - `q=author:username+type:issue+state:open`
  - `q=repo:owner/repo+label:bug`

#### 搜索代码
- **端点**: `GET /search/code`
- **速率限制**: 10 请求/分钟 (认证)
- **限制**: 只能搜索 4,000 个仓库

### Issues 和 PRs 端点

#### 列出仓库 Issues
- **端点**: `GET /repos/{owner}/{repo}/issues`
- **参数**: `state`, `labels`, `sort`, `direction`
- **注意**: 返回包括 Issues 和 PRs

#### 列出仓库 PRs
- **端点**: `GET /repos/{owner}/{repo}/pulls`
- **参数**: `state`, `head`, `base`, `sort`

#### 获取单个 Issue/PR
- **端点**: `GET /repos/{owner}/{repo}/issues/{issue_number}`
- **端点**: `GET /repos/{owner}/{repo}/pulls/{pull_number}`

### 文件内容端点

#### 获取文件内容
- **端点**: `GET /repos/{owner}/{repo}/contents/{path}`
- **参数**: `ref` (分支/标签/提交)
- **响应**: Base64 编码内容 + 元数据
- **文件大小限制**: 
  - ≤1MB: 完整支持
  - 1-100MB: 仅支持 raw 格式
  - >100MB: 不支持

#### 获取目录内容
- **端点**: `GET /repos/{owner}/{repo}/contents/{path}`
- **响应**: 文件/目录列表
- **限制**: 最多 1,000 个文件

## 速率限制策略

### 主要速率限制
- **认证用户**: 5,000 请求/小时
- **未认证用户**: 60 请求/小时
- **GitHub Apps**: 5,000-15,000 请求/小时

### 搜索特定限制
- **搜索端点**: 30 请求/分钟 (除代码搜索)
- **代码搜索**: 10 请求/分钟

### 二级速率限制
- **内容创建**: 80 请求/分钟, 500 请求/小时
- **并发请求**: 避免并发，建议串行请求
- **突变操作**: 请求间至少等待 1 秒

## 最佳实践

### 1. 条件请求
- 使用 `If-None-Match` (ETag) 和 `If-Modified-Since`
- 304 响应不计入速率限制

### 2. 分页处理
- 默认每页 30 条，最大 100 条
- 使用 `Link` 头进行分页导航

### 3. 错误处理
- **403**: 速率限制，检查 `X-RateLimit-*` 头
- **404**: 资源不存在
- **422**: 验证失败
- **500**: 服务器错误

### 4. 重试策略
- 遇到速率限制时:
  - 如果有 `Retry-After` 头，等待指定时间
  - 否则等待 1 分钟，然后指数退避重试

## 数据模型

### Issue 数据结构
```json
{
  "id": 1,
  "number": 1347,
  "title": "Found a bug",
  "state": "open",
  "body": "I'm having a problem with this.",
  "user": { /* 用户信息 */ },
  "labels": [ /* 标签列表 */ ],
  "assignee": { /* 分配人员 */ },
  "milestone": { /* 里程碑 */ },
  "comments": 0,
  "created_at": "2011-04-22T13:33:48Z",
  "updated_at": "2011-04-22T13:33:48Z",
  "closed_at": null,
  "pull_request": { /* 如果是 PR */ }
}
```

### PR 特定字段
```json
{
  "url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347",
  "head": { "ref": "feature-branch", "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e" },
  "base": { "ref": "main", "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e" },
  "merged": false,
  "mergeable": true,
  "rebaseable": true,
  "mergeable_state": "clean",
  "merged_by": null,
  "comments": 10,
  "review_comments": 0,
  "maintainer_can_modify": true,
  "commits": 3,
  "additions": 100,
  "deletions": 3,
  "changed_files": 5
}
```

### 文件内容响应
```json
{
  "type": "file",
  "encoding": "base64",
  "size": 5362,
  "name": "README.md",
  "path": "README.md",
  "content": "base64-encoded-content",
  "sha": "3d21ec53a331a6f037a91c368710b99387d012c1",
  "url": "https://api.github.com/repos/octocat/Hello-World/contents/README.md",
  "git_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs/3d21ec53a331a6f037a91c368710b99387d012c1",
  "html_url": "https://github.com/octocat/Hello-World/blob/master/README.md",
  "download_url": "https://raw.githubusercontent.com/octocat/Hello-World/master/README.md"
}
```

## 限制和约束

### 搜索限制
- 查询长度: ≤256 字符
- 逻辑运算符: ≤5 个 AND/OR/NOT
- 搜索范围: ≤4,000 个仓库

### 文件限制
- 目录内容: ≤1,000 个文件
- 文件大小: ≤100MB
- 超时: 查询可能超时，返回部分结果

### 访问限制
- 私有数据需要相应权限
- 组织数据需要组织成员身份

## 安全考虑

1. **令牌安全**: 永不暴露客户端代码中
2. **权限最小化**: 使用所需最小权限的令牌
3. **错误处理**: 妥善处理认证错误和权限错误
4. **日志记录**: 避免记录敏感令牌信息

## 参考链接

- [GitHub REST API 文档](https://docs.github.com/en/rest)
- [速率限制文档](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- [最佳实践](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)