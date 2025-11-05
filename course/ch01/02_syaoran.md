# CH01 笔记卡 - syaoran

> 提交时间：2025-11-03 21:25:05

## MCP介绍

### 什么是MCP？

mcp协议由三部分组成，主机（host），客户端（client），服务器（server）。

Model Context Protocol (MCP) 是一种协议，它允许大型语言模型（LLMs）访问自定义的工具和服务。简单来说它规定了LLM与MCP Server之间的通信协议，包括请求格式、响应格式、错误处理等。

**主机**：支持mcp的应用，如clude、trae、Cherry Studio等。

**客户端**：将用户的需求转换成服务器可以理解的格式，发送给服务器。

**服务器**：执行某些具体的功能的集合，如打开浏览器，搜索文件等类似一个小工具。服务器可以分为两种，本地服务器与远程服务器。本地服务器将工具下载至本地并执行，远程服务器则是其他设备上执行，将得到结果返回至客户端。

MCP使用JSON-RPC 2.0来作为传输的格式。使用see或stdio实现通信功能。简单来说MCP协议告诉了大模型去执行哪些功能，并将结果用特定的格式给用户。

主机创建客户端，客户端将用户的请求发送给服务器，服务器执行任务，将结果返回给客户端，客户端将结果展示给用户。

## 为什么是MCP

没有MCP之前如何使用的？各自定义自己的规范，假设你使用了10个anget，每个anget由不同的人创建，当其中某个anget接口变化时，你对应的也要变化。

开发者不必关心用户给什么的指令，只需要满足mcp服务器的格式即可。统一个时候，让开发者能更快的开发出各种各样的mcp服务器。简化了开发流程，简化用户使用流程。

MCP扩展了大模型的功能，早期的大模型只能对话，你问它答，后面出现了anget，于是大模型能自己执行功能了。mcp统一了调用外部资源的方式，实现更多功能。

## MCP缺点

MCP使用rcp，安全性不够。

## MCP资源

- [MCP源](https://www.mcp.bar/)
- [ModelScope MCP](https://www.modelscope.cn/mcp)
- [Cherry Studio MCP](https://github.com/CherryHQ/cherry-studio)
- [Smithery MCP](https://smithery.ai/)
