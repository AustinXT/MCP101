"""
我的第一个 MCP Server
提供基础工具和资源示例
"""

from fastmcp import FastMCP

# 创建 MCP 服务实例
# 参数：服务名称（会显示给客户端）
mcp = FastMCP("My First MCP Server")

# ============================================
# 工具定义（Tools）
# ============================================

@mcp.tool()
def echo(text: str) -> str:
    """
    回显工具：返回用户输入的文本

    参数：
        text: 要回显的文本

    返回：
        原样返回输入的文本

    来源：基于 MCP Tool 规范实现
    """
    return f"你说：{text}"


@mcp.tool()
def add(a: int, b: int) -> int:
    """
    加法计算器：计算两个整数的和

    参数：
        a: 第一个加数
        b: 第二个加数

    返回：
        两数之和

    来源：基于 MCP Tool 规范实现
    """
    result = a + b
    return result


# ============================================
# 资源定义（Resources）
# ============================================

@mcp.resource("file://notes/hello.txt")
def read_hello() -> str:
    """
    读取欢迎文件（静态资源）

    URI: file://notes/hello.txt
    """
    try:
        with open("notes/hello.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"错误：{str(e)}"


@mcp.resource("file://notes/{filename}")
def read_note(filename: str) -> str:
    """
    读取指定的笔记文件（动态资源）

    这是一个参数化资源，支持读取 notes/ 目录下的任意 .txt 文件

    参数：
        filename: 文件名（例如：todo.txt, python.txt）

    URI 示例：
        - file://notes/todo.txt
        - file://notes/python.txt

    来源：基于 MCP Resource 规范的动态资源实现
    """
    # 安全检查：防止路径遍历攻击
    if ".." in filename or "/" in filename:
        return "错误：非法文件名，不允许包含 '..' 或 '/'"

    filepath = f"notes/{filename}"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return f"文件：{filename}\n\n{content}"
    except FileNotFoundError:
        return f"错误：文件 {filename} 不存在"
    except Exception as e:
        return f"错误：读取失败 - {str(e)}"


@mcp.prompt()
def code_review(language: str) -> str:
    """生成代码审查提示"""
    return f"请审查以下 {language} 代码..."

# ============================================
# 启动服务
# ============================================

if __name__ == "__main__":
    # 运行 MCP 服务器
    # fastmcp 会自动处理：
    # - 初始化握手（initialize）
    # - 能力协商（capabilities negotiation）
    # - 工具列表（tools/list）
    # - 工具调用（tools/call）
    # - 资源列表（resources/list）
    # - 资源读取（resources/read）
    mcp.run()