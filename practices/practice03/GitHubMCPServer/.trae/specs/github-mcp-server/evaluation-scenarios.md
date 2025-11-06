# GitHub MCP Server 评估场景和测试用例

## 1. 复杂评估场景

### 场景 1: 完整的代码审查工作流
**目标**: 模拟真实的代码审查过程

**步骤**:
1. **发现需要审查的 PRs**
   ```json
   {
     "tool": "list_pull_requests",
     "input": {
       "repository": "facebook/react",
       "state": "open",
       "sort": "created",
       "order": "desc",
       "max_results": 10
     }
   }
   ```

2. **选择特定 PR 进行详细审查**
   ```json
   {
     "tool": "get_pull_request_details", 
     "input": {
       "repository": "facebook/react",
       "pull_number": 26875  // 从第一步结果中选择
     }
   }
   ```

3. **查看更改的文件内容**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "facebook/react",
       "file_path": "packages/react-dom/index.js",
       "ref": "pull/26875/head"
     }
   }
   ```

4. **搜索相关的 Issues 和讨论**
   ```json
   {
     "tool": "search_issues",
     "input": {
       "query": "hydration error ReactDOM",
       "repository": "facebook/react",
       "state": "open"
     }
   }
   ```

5. **查看相关的文档文件**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "facebook/react",
       "file_path": "docs/error-decoder.md"
     }
   }
   ```

**预期结果**: Agent 能够理解 PR 的上下文、相关问题和文档，提供有意义的审查意见。

---

### 场景 2: Bug 报告调研和分析
**目标**: 帮助用户理解和解决报告的 bug

**步骤**:
1. **搜索相关的 bug reports**
   ```json
   {
     "tool": "search_issues",
     "input": {
       "query": "TypeError: Cannot read property useState",
       "state": "open"
     }
   }
   ```

2. **查看具体的 bug 报告**
   ```json
   {
     "tool": "get_issue_details",
     "input": {
       "repository": "facebook/react",
       "issue_number": 24567  // 从搜索结果中选择
     }
   }
   ```

3. **查看相关的源代码文件**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "facebook/react", 
       "file_path": "packages/react/src/ReactHooks.js"
     }
   }
   ```

4. **搜索类似的代码模式**
   ```json
   {
     "tool": "search_code",
     "input": {
       "query": "useState typeof development",
       "repository": "facebook/react"
     }
   }
   ```

5. **查看测试文件了解预期行为**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "facebook/react",
       "file_path": "fixtures/devtools/regression/__tests__/useState-test.js"
     }
   }
   ```

**预期结果**: Agent 能够分析 bug 原因，找到相关代码，并提出解决方案建议。

---

### 场景 3: 新项目技术调研
**目标**: 帮助用户了解新技术或库的使用

**步骤**:
1. **探索项目结构**
   ```json
   {
     "tool": "list_repository_contents",
     "input": {
       "repository": "vercel/next.js"
     }
   }
   ```

2. **查看主要的文档文件**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "vercel/next.js",
       "file_path": "README.md"
     }
   }
   ```

3. **查看示例代码**
   ```json
   {
     "tool": "list_repository_contents",
     "input": {
       "repository": "vercel/next.js",
       "path": "examples"
     }
   }
   ```

4. **查看具体的示例实现**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "vercel/next.js",
       "file_path": "examples/api-routes/pages/api/hello.js"
     }
   }
   ```

5. **搜索相关的讨论和最佳实践**
   ```json
   {
     "tool": "search_issues",
     "input": {
       "query": "api routes best practices",
       "repository": "vercel/next.js"
     }
   }
   ```

**预期结果**: Agent 能够提供项目概述、使用示例和最佳实践建议。

---

### 场景 4: 依赖版本冲突解决
**目标**: 帮助解决依赖冲突问题

**步骤**:
1. **查看项目的依赖配置**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "user/project",
       "file_path": "package.json"
     }
   }
   ```

2. **搜索相关的依赖问题**
   ```json
   {
     "tool": "search_issues",
     "input": {
       "query": "webpack 5 conflict peer dependencies",
       "state": "open"
     }
   }
   ```

3. **查看特定依赖库的 Issues**
   ```json
   {
     "tool": "search_issues",
     "input": {
       "query": "is:issue webpack",
       "repository": "webpack/webpack"
     }
   }
   ```

4. **查看依赖库的文档**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "webpack/webpack",
       "file_path": "README.md"
     }
   }
   ```

5. **搜索解决方案和变通方法**
   ```json
   {
     "tool": "search_code",
     "input": {
       "query": "resolve.alias webpack",
       "repository": "user/project"
     }
   }
   ```

**预期结果**: Agent 能够识别依赖冲突，找到相关问题和解决方案。

---

### 场景 5: 代码重构和优化建议
**目标**: 提供代码改进建议

**步骤**:
1. **查看需要重构的代码文件**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "user/project",
       "file_path": "src/utils/helpers.js"
     }
   }
   ```

2. **搜索类似的优化模式**
   ```json
   {
     "tool": "search_code",
     "input": {
       "query": "useMemo useCallback optimization",
       "repository": "facebook/react"
     }
   }
   ```

3. **查看相关的性能讨论**
   ```json
   {
     "tool": "search_issues",
     "input": {
       "query": "performance optimization hooks",
       "repository": "facebook/react"
     }
   }
   ```

4. **查看最佳实践文档**
   ```json
   {
     "tool": "get_file_content",
     "input": {
       "repository": "facebook/react",
       "file_path": "docs/hooks-rules.md"
     }
   }
   ```

5. **搜索具体的实现示例**
   ```json
   {
     "tool": "search_code",
     "input": {
       "query": "useMemo expensive calculation",
       "repository": "user/project"
     }
   }
   ```

**预期结果**: Agent 能够提供具体的代码优化建议和最佳实践。

## 2. 测试用例

### 单元测试用例

#### 测试 1: `search_issues` 基本功能
```python
def test_search_issues_basic():
    """测试基本的 Issues 搜索功能"""
    result = search_issues({
        "query": "bug",
        "repository": "facebook/react",
        "max_results": 5
    })
    
    assert "items" in result
    assert len(result["items"]) <= 5
    assert all("title" in item for item in result["items"])
```

#### 测试 2: `get_file_content` 文件读取
```python
def test_get_file_content_existing():
    """测试读取存在的文件"""
    content = get_file_content({
        "repository": "facebook/react",
        "file_path": "README.md"
    })
    
    assert isinstance(content, str)
    assert len(content) > 0
    assert "React" in content
```

#### 测试 3: 错误处理 - 文件不存在
```python
def test_get_file_content_not_found():
    """测试文件不存在的错误处理"""
    with pytest.raises(MCPServerError) as exc_info:
        get_file_content({
            "repository": "facebook/react",
            "file_path": "nonexistent/file.txt"
        })
    
    assert exc_info.value.code == 404
    assert "not found" in exc_info.value.message.lower()
```

#### 测试 4: 速率限制处理
```python
def test_rate_limit_handling():
    """测试速率限制的处理"""
    # 模拟速率限制响应
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.headers = {"x-ratelimit-remaining": "0"}
    
    with patch('requests.get', return_value=mock_response):
        with pytest.raises(MCPServerError) as exc_info:
            search_issues({"query": "test"})
    
    assert exc_info.value.code == 403
    assert "rate limit" in exc_info.value.message.lower()
```

#### 测试 5: 输入验证
```python
def test_input_validation():
    """测试输入参数验证"""
    with pytest.raises(MCPServerError) as exc_info:
        search_issues({})  # 缺少必需的 query 参数
    
    assert exc_info.value.code == 400
    assert "required" in exc_info.value.message.lower()
```

### 集成测试用例

#### 测试 6: 端到端工作流测试
```python
def test_end_to_end_workflow():
    """测试完整的代码审查工作流"""
    # 1. 搜索开放的 PRs
    prs = list_pull_requests({
        "repository": "facebook/react",
        "state": "open",
        "max_results": 3
    })
    
    assert len(prs["items"]) > 0
    
    # 2. 获取第一个 PR 的详情
    pr_number = prs["items"][0]["number"]
    pr_details = get_pull_request_details({
        "repository": "facebook/react",
        "pull_number": pr_number
    })
    
    assert pr_details["number"] == pr_number
    
    # 3. 查看更改的文件（如果可能）
    if pr_details["changed_files"] > 0:
        # 尝试获取第一个文件的内容
        pass  # 具体实现取决于 PR 结构
```

#### 测试 7: 缓存功能测试
```python
def test_response_caching():
    """测试响应缓存功能"""
    # 第一次请求
    start_time = time.time()
    result1 = get_file_content({
        "repository": "facebook/react", 
        "file_path": "README.md"
    })
    time1 = time.time() - start_time
    
    # 第二次请求（应该从缓存获取）
    start_time = time.time()
    result2 = get_file_content({
        "repository": "facebook/react",
        "file_path": "README.md"
    })
    time2 = time.time() - start_time
    
    assert result1 == result2
    assert time2 < time1  # 缓存应该更快
```

### 性能测试用例

#### 测试 8: 并发性能测试
```python
def test_concurrent_performance():
    """测试并发请求的性能"""
    import concurrent.futures
    
    def make_request(i):
        return get_file_content({
            "repository": "facebook/react",
            "file_path": "README.md"
        })
    
    # 并发执行 5 个请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        start_time = time.time()
        results = list(executor.map(make_request, range(5)))
        total_time = time.time() - start_time
    
    # 验证所有请求都成功
    assert all(len(result) > 0 for result in results)
    
    # 记录性能指标
    print(f"5个并发请求完成时间: {total_time:.2f}秒")
```

#### 测试 9: 速率限制适应性测试
```python
def test_rate_limit_adaptation():
    """测试速率限制的适应性"""
    # 模拟接近速率限制的情况
    remaining_requests = 2
    
    results = []
    for i in range(5):  # 尝试超过剩余限制
        try:
            result = search_issues({
                "query": f"test {i}",
                "max_results": 1
            })
            results.append(result)
        except MCPServerError as e:
            if "rate limit" in str(e).lower():
                print(f"请求 {i+1} 被速率限制正确阻止")
                break
    
    assert len(results) <= remaining_requests
```

## 3. 验证标准

### 功能验证
- [ ] 所有工具都能正确响应
- [ ] 错误处理符合预期
- [ ] 速率限制正确处理
- [ ] 缓存功能正常工作
- [ ] 输入验证有效

### 性能验证  
- [ ] 单个请求响应时间 < 2秒
- [ ] 并发处理能力 > 5请求/秒
- [ ] 内存使用 < 100MB
- [ ] 缓存命中率 > 80%

### 用户体验验证
- [ ] 错误信息清晰可操作
- [ ] 响应格式易于理解
- [ ] 工具协同工作流畅
- [ ] 速率限制提示有帮助

## 4. 测试数据准备

### 测试仓库列表
```python
TEST_REPOSITORIES = [
    "facebook/react",          # 大型活跃项目
    "vercel/next.js",          # 流行框架
    "axios/axios",             # 常用库
    "user/small-project",      # 小型测试项目
    "organization/private-repo" # 私有仓库测试
]
```

### 测试文件列表
```python
TEST_FILES = [
    "README.md",
    "package.json",
    "src/index.js",
    "docs/getting-started.md",
    "examples/basic/App.js"
]
```

### 测试搜索查询
```python
TEST_SEARCH_QUERIES = [
    "bug",
    "feature request",
    "documentation",
    "performance",
    "security vulnerability"
]
```

## 5. 持续集成配置

### GitHub Actions 配置
```yaml
name: GitHub MCP Server Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run unit tests
      run: pytest tests/unit/ -v
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Run integration tests
      run: pytest tests/integration/ -v
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Run performance tests
      run: pytest tests/performance/ -v
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

这个评估场景和测试用例文档提供了全面的测试覆盖，确保 GitHub MCP Server 在各种使用场景下都能正常工作。